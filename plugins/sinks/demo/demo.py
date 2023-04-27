import time
import logging

def execute(config, get_items, register_callback, do_stop):
    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("demo sink plugin disabled")
        return
    
    logging.info("Starting demo sink")

    register_callback(my_callback)

    while not do_stop():
        print("Current SMA values:")
        for key, value in get_items().items():
            print(f"Key: {key}, Value: {value}")

        time.sleep(5)

    logging.info("Stopping demo sink")

def my_callback(key, value):
    logging.debug(f"Key {key} was updated with value {value}")