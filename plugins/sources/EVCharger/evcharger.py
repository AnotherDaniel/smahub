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
from utils.smasensors import register_sensor_dict, get_parameter_unit


def env_vars(config):
    if os.environ.get('EVCHARGER_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('EVCHARGER_ENABLED')
    if os.environ.get('EVCHARGER_ADDRESS'):
        config['server']['address'] = os.environ.get('EVCHARGER_ADDRESS')
    if os.environ.get('EVCHARGER_PROTOCOL'):
        config['server']['protocol'] = os.environ.get('EVCHARGER_PROTOCOL')
    if os.environ.get('EVCHARGER_VERIFYTLS'):
        config['server']['verifyTls'] = os.environ.get('EVCHARGER_VERIFYTLS')
    if os.environ.get('EVCHARGER_USER'):
        config['server']['username'] = os.environ.get('EVCHARGER_USER')
    if os.environ.get('EVCHARGER_PASSWORD'):
        config['server']['password'] = os.environ.get('EVCHARGER_PASSWORD')
    if os.environ.get('EVCHARGER_UPDATEFREQ'):
        config['behavior']['updateFreq'] = os.environ.get('EVCHARGER_UPDATEFREQ')
    if os.environ.get('EVCHARGER_PREFIX'):
        config['behavior']['sensorPrefix'] = os.environ.get('EVCHARGER_PREFIX')


def execute(config, add_data, dostop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("EV Charger plugin disabled")
        return

    logging.info("Starting EV Chargersource")

    # register ha sensor definitions
    register_sensor_dict('SENSORS_EVCHARGER', SENSORS_EVCHARGER)

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
        requests.packages.urllib3.disable_warnings()

    # Login & Extract Access-Token
    try:
        response = session.post(loginurl, data=postdata, timeout=5, verify=verify_tls)
    except requests.exceptions.ConnectTimeout:
        logging.fatal(f"Charger not reachable via HTTP: {config.get('server', 'address')}")
        return
    except requests.exceptions.ConnectionError as e:
        logging.fatal(f"Charger connection error: {e.args[0]}")
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
    url = f"{config.get('server', 'protocol')}://{config.get('server', 'address')}/api/v1/plants/Plant:1/devices/IGULD:SELF"
    response = session.get(url, headers=headers, verify=verify_tls)
    dev = response.json()

    DeviceInfo = {}
    DeviceInfo['name'] = dev['product']
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
                name = f"{d['channelId'].replace('Measurement.', '').replace('[]', '')}"
                # dname is name, prefixed with device prefix and serial number
                dname = f"{config.get('behavior', 'sensorPrefix')}{DeviceInfo['identifiers']}.{name}"
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

            time.sleep(int(config.get('behavior', 'updateFreq')))

        except TimeoutError:
            logging.warning("Got TimeoutError - retrying")
            pass

        except Exception as e:
            logging.error(f"Got error {e} - retrying")
            pass

    logging.info("Stopping EV Charger source")


'''
Home Assistant MQTT autodiscovery sensor definitions for TripowerX
'''
SENSORS_EVCHARGER = [
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
        'key': "ChaSess.WhIn",
        'enabled': "true",
        'name': "Charging session consumption",
        'device_class': "energy",
        'icon': "mdi:counter",
        'unit_of_measurement': "Wh",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "Chrg.ModSw",
        'enabled': "true",
        'name': "Charge mode switch",
    },
    {
        'key': "GridMs.A.phsA",
        'enabled': "true",
        'name': "Phase 1 grid current",
        'device_class': "current",
        'icon': "mdi:current-ac",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.A.phsB",
        'enabled': "true",
        'name': "Phase 2 grid current",
        'device_class': "current",
        'icon': "mdi:current-ac",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.A.phsC",
        'enabled': "true",
        'name': "Phase 3 grid current",
        'device_class': "current",
        'icon': "mdi:current-ac",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.Hz",
        'enabled': "true",
        'name': "Grid frequency",
        'device_class': "frequency",
        'icon': "mdi:sine-wave",
        'unit_of_measurement': "Hz",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.PhV.phsA",
        'enabled': "true",
        'name': "Phase 1 grid voltage",
        'device_class': "voltage",
        'icon': "mdi:flash-triangle-outline",
        'unit_of_measurement': "V",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.PhV.phsB",
        'enabled': "true",
        'name': "Phase 2 grid voltage",
        'device_class': "voltage",
        'icon': "mdi:flash-triangle-outline",
        'unit_of_measurement': "V",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.PhV.phsC",
        'enabled': "true",
        'name': "Phase 3 grid voltage",
        'device_class': "voltage",
        'icon': "mdi:flash-triangle-outline",
        'unit_of_measurement': "V",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotPF",
        'enabled': "true",
        'name': "Grid displacement factor",
    },
    {
        'key': "GridMs.TotVA",
        'enabled': "true",
        'name': "Apparent power",
        'device_class': "apparent_power",
        'icon': "mdi:home-lightning-bolt-outline",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "GridMs.TotVAr",
        'enabled': "true",
        'name': "Reactive power",
        'device_class': "reactive_power",
        'icon': "mdi:home-lightning-bolt-outline",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "InOut.GI1",
        'enabled': "true",
        'name': "Digital group input",
    },
    {
        'key': "Metering.GridMs.TotWIn",
        'enabled': "true",
        'name': "Power",
        'device_class': "power",
        'icon': "mdi:home-lightning-bolt-outline",
        'unit_of_measurement': "W",
    },
    {
        'key': "Metering.GridMs.TotWIn.ChaSta",
        'enabled': "true",
        'name': "Power (chargepoint)",
        'device_class': "power",
        'icon': "mdi:home-lightning-bolt-outline",
        'unit_of_measurement': "W",
    },
    {
        'key': "Metering.GridMs.TotWhIn",
        'enabled': "true",
        'name': "Consumption",
        'device_class': "energy",
        'icon': "mdi:counter",
        'unit_of_measurement': "Wh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
    },
    {
        'key': "Metering.GridMs.TotWhIn.ChaSta",
        'enabled': "true",
        'name': "Consumption (chargepoint)",
        'device_class': "energy",
        'icon': "mdi:counter",
        'unit_of_measurement': "Wh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
    },
    {
        'key': "Operation.EVeh.ChaStt",
        'enabled': "true",
        'name': "Vehicle charging status",
    },
    {
        'key': "Operation.EVeh.Health",
        'enabled': "true",
        'name': "Vehicle health",
    },
    {
        'key': "Operation.Evt.Msg",
        'enabled': "true",
        'name': "Status message",
    },
    {
        'key': "Operation.Health",
        'enabled': "true",
        'name': "Health",
    },
    {
        'key': "Operation.WMaxLimNom",
        'enabled': "false",
        'name': "Power Limit (Nom)",
    },
    {
        'key': "Operation.WMaxLimSrc",
        'enabled': "false",
        'name': "Power Limit (Src)",
    },
    {
        'key': "Wl.AcqStt",
        'enabled': "false",
        'name': "Wifi scan status",
    },
    {
        'key': "Wl.ConnStt",
        'enabled': "false",
        'name': "Wifi connection status",
    },
    {
        'key': "Wl.SigPwr",
        'enabled': "false",
        'name': "Wifi signal strength",
    },
    {
        'key': "Wl.SoftAcsConnStt",
        'enabled': "false",
        'name': "Wifi soft ap status",
    },
    {
        'key': "Setpoint.PlantControl.PCC.ChrgActCnt",
        'enabled': "false",
        'name': "PlantControl PCC ChrgActCnt",
    },

]