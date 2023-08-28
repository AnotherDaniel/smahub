'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.smahelpers import parameter_unit, isfloat
from utils.smasensors import register_sensor_dict


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
        config['server']['updateFreq'] = int(os.environ.get('TRIPOWERX_UPDATEFREQ'))
    if os.environ.get('TRIPOWERX_PREFIX'):
        config['server']['sensorPrefix'] = os.environ.get('TRIPOWERX_PREFIX')

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

    loginurl = f"{config.get('server','protocol')}://{config.get('server','address')}/api/v1/token"
    postdata = {'grant_type': 'password',
                'username': config.get('server', 'username'),
                'password': config.get('server', 'password'),
                }
    verify_tls = config.get('server', 'verifyTls').lower() == 'true'

    if not verify_tls:
        requests.packages.urllib3.disable_warnings()

    # Login & Extract Access-Token
    try:
        response = session.post(loginurl, data=postdata, timeout=5, verify=verify_tls)
    except requests.exceptions.ConnectTimeout as e:
        logging.fatal(f"Inverter not reachable via HTTP: {config.get('server', 'address')}")
        return
    except requests.exceptions.ConnectionError as e:
        logging.fatal(f"Inverter connection error: {e.args[0]}")
        return

    if ("Content-Length" in response.headers and response.headers["Content-Length"] == '0'):
        logging.fatal("Username or Password wrong")
        return
    if (404 == response.status_code):
        logging.fatal(f"HTTP connection to {config.get('server', 'address')} refused (status 404)")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}

    # Request Device Info
    url = f"{config.get('server','protocol')}://{config.get('server','address')}/api/v1/plants/Plant:1/devices/IGULD:SELF"
    response = session.get(url, headers=headers, verify=verify_tls)
    dev = response.json()

    DeviceInfo = {}
    DeviceInfo['name'] = dev['product']
    DeviceInfo['configuration_url'] = f"{config.get('server','protocol')}://{config.get('server', 'address')}"
    DeviceInfo['identifiers'] = dev['serial']
    DeviceInfo['model'] = f"{dev['vendor']}-{dev['product']}"
    DeviceInfo['manufacturer'] = dev['vendor']
    DeviceInfo['sw_version'] = dev['firmwareVersion']

    time.sleep(1)

    while not dostop():
        for key, value in DeviceInfo.items():
            dname = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.device_info.{key}"
            logging.debug(dname+': ' + value)
            add_data(dname, value)

        try:
            url = f"{config.get('server','protocol')}://{config.get('server', 'address')}/api/v1/measurements/live"
            response = session.post(url, headers=headers, data='[{"componentId":"IGULD:SELF"}]', verify=verify_tls)

            # Check if a new acccess token is neccesary (TODO use refresh token)
            if (response.status_code == 401):
                logging.info(f"Got {response.status_code} - trying reauth")
                response = requests.post(loginurl, data=postdata, verify=verify_tls)
                token = response.json()['access_token']
                headers = {"Authorization": "Bearer " + token}
                continue

            data = response.json()

            for d in data:
                # name is the generic parameter/measurement name
                name = f"{d['channelId'].replace('Measurement.','').replace('[]', '')}"
                # dname is name, prefixed with device prefix and serial number
                dname = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.{name}"
                if "value" in d['values'][0]:
                    v = d['values'][0]['value']
                    if isfloat(v):
                        v = round(v, 2)
                    unit = parameter_unit(name)
                    if unit:
                        add_data(dname, (v, unit))
                    else:
                        add_data(dname, v)

                elif "values" in d['values'][0]:
                    for idx in range(0, len(d['values'][0]['values'])):
                        v = d['values'][0]['values'][idx]
                        if isfloat(v):
                            v = round(v, 2)
                        idxname = dname + "." + str(idx + 1)
                        unit = parameter_unit(name)
                        if unit:
                            add_data(idxname, (v, unit))
                        else:
                            add_data(idxname, v)
                else:
                    logging.debug(f"value of {name} is currently not availably (nighttime?)")
                    pass

            time.sleep(int(config.get('server', 'updateFreq')))

        except TimeoutError:
            logging.warning(f"Got TimeoutError - retrying")
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
        'name': "Device name",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.identifiers",
        'name': "Device serial",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.model",
        'name': "Device model",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.manufacturer",
        'name': "Device manufacturer",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.sw_version",
        'name': "Device SW version",
        'entity_category': "diagnostic",
    },

    # configuration and status data
    {
        'key': "GridGuard.Cntry",
        'name': "Country standard set",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFEEI",
        'name': "EEI displacement power factor",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFExt",
        'name': "Excitation type of cos φ",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPFPrc",
        'name': "Displacement power factor",
        'suggested_display_precision': 2,
    },
    {
        'key': "InOut.GI1",
        'name': "Digital group input",
        'suggested_display_precision': 2,
    },
    {
        'key': "Inverter.VArModCfg.PFCtlVolCfg.Stt",
        'name': "cos φ(V), status",
        'suggested_display_precision': 2,
    },
        {
        'key': "Operation.BckStt",
        'name': "Backup mode status",
    },
    {
        'key': "Operation.DrtStt",
        'name': "Reason for derating",
    },
    {
        'key': "Operation.Evt.Dsc",
        'name': "Fault correction measure",
    },
    {
        'key': "Operation.Evt.Msg",
        'name': "Message",
    },
    {
        'key': "Operation.EvtCntIstl",
        'name': "Number of events for installer",
    },
    {
        'key': "Operation.EvtCntUsr",
        'name': "Number of events for user",
    },
    {
        'key': "Operation.Evt.EvtNo",
        'name': "Current event number for manufacturer",
    },
    {
        'key': "Operation.GriSwCnt",
        'name': "Number of grid connections",
    },
    {
        'key': "Operation.GriSwStt",
        'name': "Grid relay/contactor",
    },
    {
        'key': "Operation.Health",
        'name': "Condition",
    },
    {
        'key': "Operation.OpStt",
        'name': "General operating status",
    },
    {
        'key': "Operation.HealthStt.Ok",
        'name': "Nominal power in Ok Mode",
        'unit_of_measurement': "kW",
    },
    {
        'key': "Operation.PvGriConn",
        'name': "Plant mains connection",
    },
    {
        'key': "Operation.RstrLokStt",
        'name': "Block status",
    },
    {
        'key': "Operation.RunStt",
        'name': "Operating status",
    },
    {
        'key': "Operation.StandbyStt",
        'name': "Standby status",
    },
    {
        'key': "Operation.VArCtl.VArModAct",
        'name': "Active reactive power range",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.VArCtl.VArModStt",
        'name': "Active reactive power behavior",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.WMaxLimSrc",
        'name': "Source of maximum active power setpoint",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.WMinLimSrc",
        'name': "Source of minimum active power setpoint",
        'suggested_display_precision': 2,
    },
    {
        'key': "SunSpecSig.SunSpecTx",
        'name': "SunSpec life sign",
        'suggested_display_precision': 2,
    },
    {
        'key': "Upd.Stt",
        'name': "Status of the firmware update",
        'suggested_display_precision': 2,
    },
    {
        'key': "WebConn.Stt",
        'name': "Status of the Webconnect functionality",
        'suggested_display_precision': 2,
    },
    {
        'key': "Wl.ConnStt",
        'name': "Wi-Fi connection status",
        'suggested_display_precision': 2,
    },
    {
        'key': "Wl.SigPwr",
        'name': "Signal strength of the selected network",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "Setpoint.PlantControl.InOut.DigOut",
        'name': "Digital output",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.HealthStt.Alm",
        'name': "Nominal power in Fault Mode",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "Operation.HealthStt.Wrn",
        'name': "Nominal power in Warning Mode",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'icon': "mdi:home-lightning-bolt-outline",
    },

    # string-specific measurements
    {
        'key': "Coolsys.Inverter.TmpVal.1",
        'name': "Inverter temperature string 1",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "Coolsys.Inverter.TmpVal.2",
        'name': "Inverter temperature string 2",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "Coolsys.Inverter.TmpVal.3",
        'name': "Inverter temperature string 3",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'device_class': "temperature",
        'unit_of_measurement': "°C",
        'icon': "mdi:thermometer",
    },
    {
        'key': "DcMs.Amp.1",
        'name': "DC current input string 1",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },
    {
        'key': "DcMs.Amp.2",
        'name': "DC current input string 2",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },
    {
        'key': "DcMs.Amp.3",
        'name': "DC current input string 3",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'device_class': "current",
        'unit_of_measurement': "A",
        'icon': "mdi:current-dc",
    },

    {
        'key': "DcMs.Vol.1",
        'name': "DC voltage input string 1",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Vol.2",
        'name': "DC voltage input string 2",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Vol.3",
        'name': "DC voltage input string 3",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "DcMs.Watt.1",
        'name': "DC power input string 1",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "DcMs.Watt.2",
        'name': "DC power input string 2",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "DcMs.Watt.3",
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
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsA",
        'name': "Phase 1 grid current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'device_class': "current",
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsB",
        'name': "Phase 1 grid current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'device_class': "current",
        'icon': "mdi:current-ac",
        'key': "GridMs.A.phsC",
        'name': "Phase 3 grid current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "GridMs.Hz",
        'name': "Grid frequency",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Hz",
        'device_class': "frequency",
        'state_class': "measurement",
        'icon': "mdi:sine-wave",
    },
    {
        'key': "GridMs.PhV.phsA",
        'name': "Phase 1 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsA2B",
        'name': "Phase 1to2 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsB",
        'name': "Phase 2 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsB2C",
        'name': "Phase 2to3 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsC",
        'name': "Phase 3 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'key': "GridMs.PhV.phsC2A",
        'name': "Phase 3to1 grid voltage",
        'suggested_display_precision': 2,
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
    },
    {
        'device_class': "current",
        'icon': "mdi:current-ac",
        'key': "GridMs.TotA",
        'name': "Grid current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "GridMs.TotVA",
        'name': "Apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotVAr",
        'name': "Reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotW",
        'name': "Power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.TotW.Pv",
        'name': "Power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsA",
        'name': "Phase 1 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsB",
        'name': "Phase 2 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VA.phsC",
        'name': "Phase 3 apparent power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VA",
        'device_class': "apparent_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsA",
        'name': "Phase 1 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsB",
        'name': "Phase 2 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.VAr.phsC",
        'name': "Phase 3 reactive power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "VAR",
        'device_class': "reactive_power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsA",
        'name': "Phase 1 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsB",
        'name': "Phase 2 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "GridMs.W.phsC",
        'name': "Phase 3 power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'device_class': "current",
        'icon': "mdi:current-dc",
        'key': "Isolation.FltA",
        'name': "Residual current",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'unit_of_measurement': "A",
    },
    {
        'key': "Isolation.LeakRis",
        'name': "Insulation resistance",
        'suggested_display_precision': 2,
        'unit_of_measurement': "kOhm",
        'icon': "mdi:omega",
    },
    {
        'key': "Metering.TotFeedTms",
        'name': "Feed-in time",
        'suggested_display_precision': 2,
        'unit_of_measurement': "s",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotOpTms",
        'name': "Operating time",
        'suggested_display_precision': 2,
        'unit_of_measurement': "s",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotWhOut",
        'name': "Total yield",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Wh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Metering.TotWhOut.Pv",
        'name': "Total PV yield",
        'suggested_display_precision': 2,
        'unit_of_measurement': "Wh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "PvGen.PvW",
        'name': "PV generation power",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
        'device_class': "power",
        'state_class': "measurement",
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "PvGen.PvWh",
        'name': "Meter count and PV gen. meter",
        'suggested_display_precision': 2,
        'unit_of_measurement': "kWh",
        'device_class': "energy",
        'state_class': "total_increasing",
        'icon': "mdi:counter",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.W",
        'name': "Active power limitation by PV system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "W",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.PFCtlComCfg.PF",
        'name': "External cos φ setpoint specification, cos φ setpoint for active power output",
        'suggested_display_precision': 4,
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.PFCtlComCfg.PFExt",
        'name': "External cos φ setpoint specification, excitation type for active power output",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.VArModCfg.VArCtlComCfg.VArNom",
        'name': "Standardized reactive power setpoint by system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.WNom",
        'name': "Normalized active power limitation by PV system control",
        'suggested_display_precision': 2,
        'unit_of_measurement': "%",
    },
    {
        'key': "SunSpecSig.SunSpecTx.1",
        'name': "SunSpec life sign [1]",
    },
    {
        'key': "Wl.AcqStt",
        'name': "Status of Wi-Fi scan",
    },
    {
        'key': "Wl.SoftAcsConnStt",
        'name': "Soft Access Point status",
    },
]
