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
        config['server']['updatefreq'] = int(os.environ.get('MQTT_UPDATEFREQ'))

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

    # Either us the callback, or have regular publication in below loop... 
    register_callback(my_callback)

    while not do_stop():
        # for _, value in get_items().items():
        #     topic = str(value[0]).replace(".", "/")
        #     message = str(value[1])
        #     client.publish(topic, message)
        # time.sleep(int(config.get('server', 'updatefreq')))
        time.sleep(1)

    # Disconnect from the broker
    client.disconnect()
    logging.info("Stopping MQTT sink")


def my_callback(key, value):
    global client
    topic = str(key).replace(".", "/")
    message = str(value)
    client.publish(topic, message)
