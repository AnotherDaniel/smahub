import os
import time
import logging
from utils.smasensors import register_sensor_dict


def env_vars(config):
    if os.environ.get('DEMOSOURCE_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('DEMOSOURCE_ENABLED')


def execute(config, add_data, dostop):
    env_vars(config)

    # register ha sensor definitions
    register_sensor_dict('SENSORS_DEMO', SENSORS_DEMO)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("demo source plugin disabled")
        return

    logging.info("Starting demo source")

    i = 1
    while not dostop():
        add_data('demoValue', i)
        i = i+1
        print(config.get('content', 'message'))
        time.sleep(5)

    logging.info("Stopping demo source")


'''
Home Assistant MQTT autodiscovery sensor definitions for Demo plugin
'''
SENSORS_DEMO = [
    {
        'key': "demoValue",
        'name': "Demo value",
        'entity_category': "diagnostic",
    },
]