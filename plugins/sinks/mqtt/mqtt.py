import os
import time
import logging
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="smahub", transport='tcp', protocol=mqtt.MQTTv311, clean_session=False)
pubunits = False


def env_vars(config):
    if os.environ.get('MQTT_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('MQTT_ENABLED')
    if os.environ.get('MQTT_ADDRESS'):
        config['server']['address'] = os.environ.get('MQTT_ADDRESS')
    if os.environ.get('MQTT_PORT'):
        config['server']['port'] = os.environ.get('MQTT_PORT')
    if os.environ.get('MQTT_USER'):
        config['server']['username'] = os.environ.get('MQTT_USER')
    if os.environ.get('MQTT_PASSWORD'):
        config['server']['password'] = os.environ.get('MQTT_PASSWORD')
    if os.environ.get('MQTT_UPDATEFREQ'):
        config['behavior']['updatefreq'] = os.environ.get('MQTT_UPDATEFREQ')
    if os.environ.get('MQTT_PUBLISHUNITS'):
        config['behavior']['publish_units'] = os.environ.get(
            'MQTT_PUBLISHUNITS')


def execute(config, get_items, register_callback, do_stop):
    env_vars(config)
    global pubunits
    pubunits = str(config['behavior']['publish_units']).lower() == "true"

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("MQTT sink plugin disabled")
        return

    logging.info("Starting MQTT sink")

    # Create a MQTT client instance and connect to broker
    global client
    if config['server']['username']:
        client.username_pw_set(config['server']['username'], config['server']['password'])
    try:
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.connect(config.get('server', 'address'), int(config.get('server', 'port')))
        logging.debug(f"MQTT sink connected to {config.get('server', 'address')}:{str(config.get('server', 'port'))}")
    except ValueError as exc:
        logging.fatal(f"MQTT broker configuration error: {str(exc)}")
        return
    except ConnectionError:
        logging.fatal(f"MQTT broker not reachable at address: {config.get('server', 'address')}: {str(config.get('server', 'port'))}")
        return
    except Exception as exc:
        logging.fatal(f"MQTT broker unknown error: {str(exc)}")
        return

    # We only publish data on change
    register_callback(my_callback)

    i = 0
    while not do_stop():
        # while we're normally only publishing on change (see callback below), once a minute (default) push out everything
        if i % int(config['behavior']['updatefreq']) == 0:
            for key, value in get_items().items():
                topic = str(key).replace(".", "/")
                publish(topic, value)

        i = i+1
        time.sleep(1)

    # Disconnect from the broker
    client.disconnect()
    logging.info("Stopping MQTT sink")


def publish(topic, value):
    global client, pubunits
    # only publish units if they are there and we really want to
    publish_value = value
    if isinstance(value, tuple):
        if not pubunits:
            publish_value = value[0]
    client.publish(topic, str(publish_value))


def my_callback(key, value):
    topic = str(key).replace(".", "/")
    publish(topic, value)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.debug("Connected to MQTT Broker!")
    else:
        logging.error("Failed to connect to MQTT Broker, return code %d\n", rc)


def on_disconnect(client, userdata, rc):
    logging.debug("Disconnected from MQTT Broker!")
    attempt_reconnect(client)


def attempt_reconnect(client, delay=2, max_delay=300):
    """Attempt to reconnect to MQTT Broker with exponential backoff."""
    while not client.is_connected():
        logging.debug("Attempting to reconnect to MQTT Broker...")
        try:
            client.reconnect()
        except ConnectionError:
            logging.debug(
                "Reconnecting to MQTT Broker failed. Waiting to retry...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)
        else:
            logging.debug("Reconnected to the MQTT broker.")
            break
