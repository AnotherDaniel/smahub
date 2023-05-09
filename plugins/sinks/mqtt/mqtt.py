'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import os
import time
import logging
import paho.mqtt.client as mqtt

client = mqtt.Client()

def env_vars(config):
    if os.environ.get('MQTT_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('MQTT_ENABLED')
    if os.environ.get('MQTT_ADDRESS'):
        config['server']['address'] = os.environ.get('MQTT_ADDRESS')
    if os.environ.get('MQTT_PORT'):
        config['server']['port'] = os.environ.get('MQTT_PORT')
    if os.environ.get('MQTT_UPDATEFREQ'):
        config['behavior']['updatefreq'] = int(os.environ.get('MQTT_UPDATEFREQ'))
    if os.environ.get('MQTT_PUBLISHUNITS'):
        config['behavior']['publish_units'] = os.environ.get('MQTT_PUBLISHUNITS')

def execute(config, get_items, register_callback, do_stop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("MQTT sink plugin disabled")
        return

    logging.info("Starting MQTT sink")

    # Create a MQTT client instance and connect to broker
    global client
    try:
        client.connect(config.get('server', 'address'), int(config.get('server', 'port')))
    except ConnectionError:
        logging.fatal(f"MQTT broker not reachable at address: {config.get('server', 'address')}: {str(config.get('server', 'port'))}")
        return

    # We only publish data on change
    register_callback(my_callback)

    i = 0
    while not do_stop():
        # while we're normally only publishing on change (see callback below), once a minute push out everything
        if i%int(config['behavior']['updatefreq']) == 0:
            for key, value in get_items().items():
                topic = str(key).replace(".", "/")
                # only publish units if they are there and we really want to
                publish_value = value if not isinstance(value, tuple) or config['behavior']['publish_units'] == 'true' else value[0]
                client.publish(topic, publish_value)

        i = i+1
        time.sleep(1)

    # Disconnect from the broker
    client.disconnect()
    logging.info("Stopping MQTT sink")


def my_callback(key, value):
    global client
    topic = str(key).replace(".", "/")
    if isinstance(value, tuple):
        client.publish(topic, value[0])
    else:
        client.publish(topic, value)
