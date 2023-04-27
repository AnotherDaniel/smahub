import time
import logging
import paho.mqtt.client as mqtt

client = mqtt.Client()

def execute(config, get_items, register_callback, do_stop):
    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("MQTT sink plugin disabled")
        return

    logging.info("Starting MQTT sink")

    # Create a MQTT client instance and connect to broker
    global client
    client.connect(config.get('server', 'address'), int(config.get('server', 'port')))

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
