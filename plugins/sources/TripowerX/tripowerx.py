'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import time
import sys
import requests
from utils.smahelpers import unit_of_measurement, isfloat

def execute(config, add_data, dostop):
    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("Tripower X plugin disabled")
        return

    logging.info("Starting Tripower X source")
    loginurl = 'http://' + config.get('server', 'address') + '/api/v1/token'
    postdata = {'grant_type': 'password',
            'username': config.get('server', 'username'),
            'password': config.get('server', 'password'),
            }

    # Login & Extract Access-Token
    try:
        x = requests.post(loginurl, data = postdata, timeout = 5)
    except requests.exceptions.ConnectTimeout:
        print("Inverter not reachable via HTTP.")
        print("Please test the following URL in a browser: " + 'http://' + config.get('server', 'address'))
        sys.exit(1)
    if ("Content-Length" in x.headers and x.headers["Content-Length"] == '0'):
        print("Username or Password wrong.")
        print("Please test the following URL in a browser: " + 'http://' + config.get('server', 'address'))
        sys.exit(1)
    token = x.json()["access_token"] 
    headers = { "Authorization" : "Bearer " + token }

    # Request Device Info
    url="http://" + config.get('server', 'address') + "/api/v1/plants/Plant:1/devices/IGULD:SELF"
    x = requests.get(url, headers = headers)
    dev = x.json()

    device_info = {}
    device_info['name'] = dev["product"]
    device_info['configuration_url'] = 'http://' + config.get('server', 'address')
    device_info['identifiers'] = dev["serial"]
    device_info['model'] = dev["vendor"]+"-" + dev["product"]
    device_info['manufacturer'] = dev["vendor"]
    device_info['sw_version'] = dev['firmwareVersion']

    time.sleep(1)

    while not dostop():
        try:
            url = 'http://' + config.get('server', 'address') + '/api/v1/measurements/live'
            x = requests.post(url, headers = headers, data='[{"componentId":"IGULD:SELF"}]')

            # Check if a new acccess token is neccesary (TODO use refresh token)
            if (x.status_code == 401):
                x = requests.post(loginurl, data = postdata)
                token = x.json()["access_token"] 
                headers = { "Authorization" : "Bearer " + token }
                continue
            
            data = x.json()

            for d in data:
                dname = config.get('server', 'sensorPrefix') + d["channelId"].replace("Measurement.","").replace("[]", "")
                if "value" in d["values"][0]:
                    v = d["values"][0]["value"]
                    if isfloat(v):
                        v = round(v,2)
                    unit = unit_of_measurement(dname)

                    logging.debug(dname+': '+str(v)+' '+unit)
                    add_data(dname, (v, unit))
                
                elif "values" in d["values"][0]:
                    for idx in range(0, len(d["values"][0]["values"])):
                        v = d["values"][0]["values"][idx]
                        if isfloat(v):
                            v = round(v, 2)
                        idxname = dname + "." + str(idx + 1)
                        unit = unit_of_measurement(dname)

                        logging.debug(idxname+': '+str(v)+' '+unit)
                        add_data(idxname, (v, unit))
                
                else:
                    logging.debug("value currently not availably (nighttime?)")
                    pass

            time.sleep(int(config.get('server', 'updatefreq')))
        except TimeoutError:
            pass

    logging.info("Stopping Tripower X source")
