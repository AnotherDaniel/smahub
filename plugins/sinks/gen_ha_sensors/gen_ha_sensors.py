import os
import time
import logging

def env_vars(config):
    if os.environ.get('GENHASENSORS_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('GENHASENSORS_ENABLED')
    if os.environ.get('GENHASENSORS_GENERATEFREQ'):
        config['generator']['generate_freq'] = os.environ.get('GENHASENSORS_GENERATEFREQ', "10")
    if os.environ.get('GENHASENSORS_FILEPREFIX'):
        config['generator']['filename_prefix'] = os.environ.get('GENHASENSORS_FILEPREFIX', "")
    # need to get a little creative for loading icons - as these use 'dynamic' names matching the respective plugin
    for icon in config['icons'].items():
        if os.environ.get(f"GENHASENSORS_{icon[0].upper()}"):
            config['icons'][icon[0]] = os.environ.get(f"GENHASENSORS_{icon[0].upper()}")

def execute(config, get_items, register_callback, do_stop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("gen_ha_sensors sink plugin disabled")
        return

    logging.info("Starting gen_ha_sensors sink")

    # start counting at 1 so that publication will not happen immediately, so sma_dict can populate a bit
    i = 1
    often = int(config['generator']['generate_freq'])
    while not do_stop():   
        # we only do this "occasionally"
        if i%often == 0:
            # first, retrieve all unique first name-sections from dictionary
            sma_items = get_items()
            unique_parts = set()
            for path in sma_items.keys():
                first_part = path.split('.')[0]
                unique_parts.add(first_part)

            for part in unique_parts:
                file_name = f"{config['generator']['filename_prefix']}{part}.yaml"
                # retrieve sub-set of sma_items that contains keys beginning with 'part' (current device)
                filtered_items = {k: v for k, v in sma_items.items() if k.split('.')[0] == part}

                try:
                    with open(file_name, 'w') as file:        
                        for key, value in filtered_items.items():
                            file.write(f"- name: {str(key).replace('.', '_')}\n")
                            file.write(f"  state_topic: \"{str(key).replace('.', '/')}\"\n")
                            
                            if config['icons'].get(part):
                                icon = config['icons'][part]
                                file.write(f"  icon: \"{icon}\"\n")

                            # if value is a tuple, first entry should be measurement and second unit
                            if isinstance(value, tuple):
                                file.write(f"  unit_of_measurement: \"{value[1]}\"\n")
                                dev_class = device_class(value[1])
                                if dev_class:
                                    file.write(f"  device_class: \"{dev_class}\"\n")
                                    file.write(f"  state_class: \"{state_class(key, value[1])}\"\n")
                
                except OSError as e:
                    logging.error(f"Error writing to file {file_name}: {e}")

        i = i+1
        time.sleep(1)

    logging.info("Stopping gen_ha_sensors sink")

# Home Assistant device class mapping, from physical unit
def device_class(unit):
    device_class = ""
    if unit == "Wh" or unit == "kWh":
        device_class = "energy"
    elif unit == "VA" or unit == "kVA":
        device_class = "apparent_power"
    elif unit == "var":
        device_class = "reactive_power"
    elif unit == "V":
        device_class = "voltage"
    elif unit == "A":
        device_class = "current"
    elif unit == "Hz":
        device_class = "frequency"
    elif unit == "W" or unit == "kW":
        device_class = "power"
    elif unit == "°C":
        device_class = "temperature"
    elif unit == "s":
        device_class = "duration"

    return device_class

# Home Assistant state class mapping, from name or unit
def state_class(name, unit):
    if 'WCtlComCfg' in name:
        return "total"
    if 'TotWh'in name or 'PvWh' in name:
        return "total_increasing"
   
    if unit == "V" or unit == "VA" or unit == "var" or unit == "W":
        return "measurement"
    if unit == "Wh" or unit == "kWh" or unit == "kVAh" or unit == "kvarh":
        return "total"
    if unit == "s":
        return "total_increasing"

   