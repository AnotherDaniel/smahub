import time
import logging

def execute(config, add_data, dostop): 
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
