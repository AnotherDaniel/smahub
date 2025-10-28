'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import os
import time
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.smahelpers import isfloat
from utils.smasensors import register_sensor_dict, get_parameter_unit


def env_vars(config):
    if os.environ.get('TRIPOWERX_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('TRIPOWERX_ENABLED')
    if os.environ.get('TRIPOWERX_ADDRESS'):
        config['server']['address'] = os.environ.get('TRIPOWERX_ADDRESS')
    if os.environ.get('TRIPOWERX_PROTOCOL'):
        config['server']['protocol'] = os.environ.get('TRIPOWERX_PROTOCOL')
    if os.environ.get('TRIPOWERX_VERIFYTLS'):
        config['server']['verifyTls'] = os.environ.get('TRIPOWERX_VERIFYTLS')
    if os.environ.get('TRIPOWERX_USER'):
        config['server']['username'] = os.environ.get('TRIPOWERX_USER')
    if os.environ.get('TRIPOWERX_PASSWORD'):
        config['server']['password'] = os.environ.get('TRIPOWERX_PASSWORD')
    if os.environ.get('TRIPOWERX_UPDATEFREQ'):
        config['behavior']['updateFreq'] = os.environ.get(
            'TRIPOWERX_UPDATEFREQ')
    if os.environ.get('TRIPOWERX_PREFIX'):
        config['behavior']['sensorPrefix'] = os.environ.get('TRIPOWERX_PREFIX')
    if os.environ.get('IDENT_POSTFIX') is not None:
        config['behavior']['identPostfix'] = os.environ.get('IDENT_POSTFIX')


def execute(config, add_data, dostop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("Tripower X plugin disabled")
        return

    logging.info("Starting Tripower X source")

    # register ha sensor definitions
    register_sensor_dict('SENSORS_TRIPOWERX', SENSORS_TRIPOWERX)

    # set up retry and backoff for connection
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    loginurl = f"{config.get('server', 'protocol')}://{config.get('server', 'address')}/api/v1/token"
    postdata = {'grant_type': 'password',
                'username': config.get('server', 'username'),
                'password': config.get('server', 'password'),
                }

    verify_tls = config.get('server', 'verifyTls').lower() == 'true'
    if not verify_tls:
        urllib3.disable_warnings()  # Use the direct import instead of requests.packages path

    # Login & Extract Access-Token
    try:
        response = session.post(loginurl, data=postdata,
                                timeout=5, verify=verify_tls)
    except requests.exceptions.ConnectTimeout:
        logging.fatal(
            f"Inverter not reachable via HTTP: {config.get('server', 'address')}")
        return
    except requests.exceptions.ConnectionError as e:
        logging.fatal(f"Inverter connection error: {e.args[0]}")
        return

    if ("Content-Length" in response.headers and response.headers["Content-Length"] == '0'):
        logging.fatal("Username or Password wrong")
        return
    if (404 == response.status_code):
        logging.fatal(
            f"HTTP connection to {config.get('server', 'address')} refused (status 404)")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}

    # Request Device Info
    url = f"{config.get('server', 'protocol')}://{config.get('server', 'address')}/api/v1/plants/Plant:1/devices/IGULD:SELF"
    response = session.get(url, headers=headers, verify=verify_tls)
    dev = response.json()

    DeviceInfo = {}
    ident_postfix = config.get('behavior', 'identPostfix', fallback='')
    DeviceInfo['name'] = dev['product'] + ident_postfix
    DeviceInfo['configuration_url'] = f"{config.get('server', 'protocol')}://{config.get('server', 'address')}"
    DeviceInfo['identifiers'] = dev['serial']
    DeviceInfo['model'] = f"{dev['vendor']}-{dev['product']}"
    DeviceInfo['manufacturer'] = dev['vendor']
    DeviceInfo['sw_version'] = dev['firmwareVersion']

    time.sleep(1)

    while not dostop():
        for key, value in DeviceInfo.items():
            dname = f"{config.get('behavior', 'sensorPrefix')}{DeviceInfo['identifiers']}.device_info.{key}"
            logging.debug(dname+': ' + value)
            add_data(dname, value)

        try:
            url = f"{config.get('server', 'protocol')}://{config.get('server', 'address')}/api/v1/measurements/live"
            response = session.post(
                url, headers=headers, data='[{"componentId":"IGULD:SELF"}]', verify=verify_tls)

            # Check if a new acccess token is neccesary (TODO use refresh token)
            if (response.status_code == 401):
                logging.info(f"Got {response.status_code} - trying reauth")
                response = requests.post(
                    loginurl, data=postdata, verify=verify_tls)
                token = response.json()['access_token']
                headers = {"Authorization": "Bearer " + token}
                continue

            data = response.json()

            for d in data:
                # name is the generic parameter/measurement name
                name = f"{d['channelId'].replace('Measurement.', '').replace('[]', '')}"
                # dname is name, prefixed with device prefix and serial number
                dname = f"{config.get('behavior', 'sensorPrefix')}{DeviceInfo['identifiers']}.{name}"
                if "value" in d['values'][0]:
                    v = d['values'][0]['value']
                    if isfloat(v):
                        try:
                            v = round(float(v), 2)
                        except Exception as e:
                            logging.error(
                                f"Error rounding value for parameter "
                                f"'{name}': value='{v}', "
                                f"type={type(v).__name__}, error: {e}")
                            raise

                    unit = get_parameter_unit('SENSORS_TRIPOWERX', name)
                    if unit:
                        add_data(dname, (v, unit))
                    else:
                        add_data(dname, v)

                elif "values" in d['values'][0]:
                    for idx in range(0, len(d['values'][0]['values'])):
                        v = d['values'][0]['values'][idx]
                        if isfloat(v):
                            try:
                                v = round(float(v), 2)
                            except Exception as e:
                                logging.error(
                                    f"Error rounding value for parameter "
                                    f"'{name}[{idx}]': value='{v}', "
                                    f"type={type(v).__name__}, error: {e}")
                                raise

                        idxname = dname + "." + str(idx + 1)
                        unit = get_parameter_unit('SENSORS_TRIPOWERX', name)
                        if unit:
                            add_data(idxname, (v, unit))
                        else:
                            add_data(idxname, v)
                else:
                    logging.debug(
                        f"value of {name} is currently not availably (nighttime?)")
                    pass

            time.sleep(int(config.get('behavior', 'updateFreq')))

        except TimeoutError:
            logging.warning("Got TimeoutError - retrying")
            pass

        except Exception as e:
            logging.error(f"Got error {e} - retrying")
            pass

    logging.info("Stopping Tripower X source")


'''
Home Assistant MQTT autodiscovery sensor definitions for TripowerX
'''
SENSORS_TRIPOWERX = [
    # device info
    {
        'key': "device_info.name",
        'enabled': "true",
        'name': "Device name",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.identifiers",
        'enabled': "true",
        'name': "Device serial",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.model",
        'enabled': "true",
        'name': "Device model",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.manufacturer",
        'enabled': "true",
        'name': "Device manufacturer",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.sw_version",
        'enabled': "true",
        'name': "Device SW version",
        'entity_category': "diagnostic",
    },

    # configuration and status data
    {
        'key': "GridGuard.Cntry",
        'enabled': "true",
        'name': "Country standard set",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFEEI",
        'enabled': "true",
        'name': "EEI displacement power factor",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFExt",
        'enabled': "true",
        'name': "Excitation type of cos φ",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFPrc",
        'enabled': "true",
        'name': "Displacement power factor",
        'suggested_display_precision': 2,
    },
    {
        'key': "InOut.GI1",
        'enabled': "true",
        'name': "Digital group input",
        'suggested_display_precision': 2,
    },
    {
        'key': "Inverter.VArModCfg.PFCtlVolCfg.Stt",
        'enabled': "true",
        'name': "cos φ(V), status",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.BckStt",
        'enabled': "true",
        'name': "Backup mode status",
    },
    {
        'key': "Operation.DrtStt",
        'enabled': "true",
        'name': "Reason for derating",
    },
    {
        'key': "Operation.Evt.Dsc",
        'enabled': "true",
        'name': "Fault correction measure",
    },
    {
        'key': "Operation.Evt.Msg",
        'enabled': "true",
        'name': "Message",
    },
    {
        'key': "Operation.EvtCntIstl",
        'enabled': "true",
        'name': "Number of events for installer",
    },
    {
        'key': "Operation.EvtCntUsr",
        'enabled': "true",
        'name': "Number of events for user",
    },
    {
        'key': "Operation.Evt.EvtNo",
        'enabled': "true",
        'name': "Current event number for manufacturer",
    },
    {
        'key': "Operation.GriSwCnt",
        'enabled': "true",
        'name': "Number of grid connections",
    },
    {
        'key': "Operation.GriSwStt",
        'enabled': "true",
        'name': "Grid relay/contactor",
    },
    {
        'key': "Operation.Health",
        'enabled': "true",
        'name': "Condition",
    },
    {
        'key': "Operation.OpStt",
        'enabled': "true",
        'name': "General operating status",
    },
    {
        'key': "Operation.HealthStt.Ok",
        'enabled': "true",
        'name': "Nominal power in Ok Mode",
        'unit_of_measurement': "kW",
    },
    {
        'key': "Operation.PvGriConn",
        'enabled': "true",
        'name': "Plant mains connection",
    },
    {
        'key': "Operation.RstrLokStt",
        'enabled': "true",
        'name': "Block status",
    },
    {
        'key': "Operation.RunStt",
        'enabled': "true",
        'name': "Operating status",
    },
    {
        'key': "Operation.StandbyStt",
        'enabled': "true",
        'name': "Standby status",
    },
    {
        'key': "Operation.VArCtl.VArModAct",
        'enabled': "true",
        'name': "Active reactive power range",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.VArCtl.VArModStt",
        'enabled': "true",
        'name': "Active reactive power behavior",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.WMaxLimSrc",
        'enabled': "true",
        'name': "Source of maximum active power setpoint",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.WMinLimSrc",
        'enabled': "true",
        'name': "Source of minimum active power setpoint",
        'suggested_display_precision': 2,
    },
    {
        'key': "SunSpecSig.SunSpecTx",
        'enabled': "true",
        'name': "SunSpec life sign",
        'suggested_display_precision': 2,
    },
    {
        'key': "Upd.Stt",
        'enabled': "true",
        'name': "Status of the firmware update",
        'suggested_display_precision': 2,
    },
    {
        'key': "WebConn.Stt",
        'enabled': "true",
        'name': "Status of the Webconnect functionality",
        'suggested_display_precision': 2,
    },
    {
        'key': "Wl.ConnStt",
        'enabled': "true",
        'name': "Wi-Fi connection status",
        'suggested_display_precision': 2,
    },
    {
        'key': "Wl.SigPwr",
        'enabled': "true",
        'name': "Signal strength of the selected network",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "Setpoint.PlantControl.InOut.DigOut",
        'enabled': "true",
        'name': "Digital output",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.HealthStt.Alm",
        'enabled': "true",
        'name': "Nominal power in Fault Mode",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "Operation.HealthStt.Wrn",
        'enabled': "true",
        'name': "Nominal power in Warning Mode",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'icon': "mdi:home-lightning-bolt-outline",
    },

    # string-specific measurements
    {
        'key': "Coolsys.Inverter.TmpVal",
        'name': "Inverter temperature",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "Coolsys.Inverter.TmpVal.1",
        'enabled': "true",
        'name': "Inverter temperature string 1",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "Coolsys.Inverter.TmpVal.2",
        'enabled': "true",
        'name': "Inverter temperature string 2",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "Coolsys.Inverter.TmpVal.3",
        'enabled': "true",
        'name': "Inverter temperature string 3",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "DcMs.Amp.1",
        'enabled': "true",
        'name': "DC current input string 1",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },
    {
        'key': "DcMs.Amp.2",
        'enabled': "true",
        'name': "DC current input string 2",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },
    {
        'key': "DcMs.Amp.3",
        'enabled': "true",
        'name': "DC current input string 3",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },

    {
        'key': "DcMs.Vol.1",
        'enabled': "true",
        'name': "DC voltage input string 1",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Vol.2",
        'enabled': "true",
        'name': "DC voltage input string 2",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Vol.3",
        'enabled': "true",
        'name': "DC voltage input string 3",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Watt.1",
        'enabled': "true",
        'name': "DC power input string 1",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "DcMs.Watt.2",
        'enabled': "true",
        'name': "DC power input string 2",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "DcMs.Watt.3",
        'enabled': "true",
        'name': "DC power input string 3",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },

    # global measurements
    {
        'device_class': "current",
        'enabled': "false",
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsA",
        'name': "Phase 1 grid current",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'device_class': "current",
        'enabled': "false",
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsB",
        'name': "Phase 1 grid current",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'device_class': "current",
        'enabled': "false",
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsC",
        'name': "Phase 3 grid current",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "GridMs.Hz",
        'enabled': "true",
        'name': "Grid frequency",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Hz",
        'device_class': "frequency",
        'state_class': "measurement",
        'icon': "mdi:sine-wave",
    },
    {
        'key': "GridMs.PhV.phsA",
        'enabled': "false",
        'name': "Phase 1 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsA2B",
        'enabled': "false",
        'name': "Phase 1to2 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsB",
        'enabled': "false",
        'name': "Phase 2 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsB2C",
        'enabled': "false",
        'name': "Phase 2to3 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsC",
        'enabled': "false",
        'name': "Phase 3 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsC2A",
        'enabled': "false",
        'name': "Phase 3to1 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'device_class': "current",
        'enabled': "true",
        'icon': "mdi:current-ac",
        'key': "GridMs.TotA",
        'name': "Grid current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "GridMs.TotVA",
        'enabled': "false",
        'name': "Apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotVAr",
        'enabled': "false",
        'name': "Reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotW",
        'enabled': "true",
        'name': "Power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotW.Pv",
        'enabled': "true",
        'name': "Power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsA",
        'enabled': "false",
        'name': "Phase 1 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsB",
        'enabled': "false",
        'name': "Phase 2 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsC",
        'enabled': "false",
        'name': "Phase 3 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsA",
        'enabled': "false",
        'name': "Phase 1 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsB",
        'enabled': "false",
        'name': "Phase 2 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsC",
        'enabled': "false",
        'name': "Phase 3 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsA",
        'enabled': "false",
        'name': "Phase 1 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsB",
        'enabled': "false",
        'name': "Phase 2 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsC",
        'enabled': "false",
        'name': "Phase 3 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'device_class': "current",
        'enabled': "false",
        'icon': "mdi:current-dc",
        'key': "Isolation.FltA",
        'name': "Residual current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "Isolation.LeakRis",
        'enabled': "false",
        'name': "Insulation resistance",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Ohm",
        'icon': "mdi:omega",
    },
    {
        'key': "Metering.TotFeedTms",
        'enabled': "true",
        'name': "Feed-in time",
        'suggested_display_precision': 2,
        'unit_of_measurement': "s",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotOpTms",
        'enabled': "true",
        'name': "Operating time",
        'suggested_display_precision': 2,
        'unit_of_measurement': "s",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotWhOut",
        'enabled': "true",
        'name': "Total yield",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Wh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotWhOut.Pv",
        'enabled': "true",
        'name': "Total PV yield",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Wh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "PvGen.PvW",
        'enabled': "true",
        'name': "PV generation power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "PvGen.PvWh",
        'enabled': "true",
        'name': "Meter count and PV gen. meter",
        'suggested_display_precision': 2,
        'unit_of_measurement': "kWh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.W",
        'enabled': "true",
        'name': "Active power limitation by PV system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.PFCtlComCfg.PF",
        'enabled': "false",
        'name': "External cos φ setpoint specification, cos φ setpoint for active power output",
        'suggested_display_precision': 4,
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.PFCtlComCfg.PFExt",
        'enabled': "false",
        'name': "External cos φ setpoint specification, excitation type for active power output",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.VArCtlComCfg.VArNom",
        'enabled': "false",
        'name': "Standardized reactive power setpoint by system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.WNom",
        'enabled': "true",
        'name': "Normalized active power limitation by PV system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "SunSpecSig.SunSpecTx.1",
        'enabled': "false",
        'name': "SunSpec life sign [1]",
    },
    {
        'key': "Wl.AcqStt",
        'enabled': "false",
        'name': "Status of Wi-Fi scan",
    },
    {
        'key': "Wl.SoftAcsConnStt",
        'enabled': "false",
        'name': "Soft Access Point status",
    },
]
