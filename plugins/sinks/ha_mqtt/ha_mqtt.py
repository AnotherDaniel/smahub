import os
import time
import logging
from ha_mqtt_discoverable import Settings
from ha_mqtt_discoverable.sensors import SensorInfo, Sensor, DeviceInfo

# store for all the ha_mqtt sensor objects
sensors = {}
device_infos = {}
mqtt_settings = {}


def env_vars(config):
    if os.environ.get('HA_MQTT_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('HA_MQTT_ENABLED')
    if os.environ.get('HA_MQTT_ADDRESS'):
        config['server']['address'] = os.environ.get('HA_MQTT_ADDRESS')
    if os.environ.get('HA_MQTT_USER'):
        config['server']['username'] = os.environ.get('HA_MQTT_USER')
    if os.environ.get('HA_MQTT_PASSWORD'):
        config['server']['password'] = os.environ.get('HA_MQTT_PASSWORD')
    if os.environ.get('HA_MQTT_UPDATEFREQ'):
        config['behavior']['updatefreq'] = int(os.environ.get('HA_MQTT_UPDATEFREQ'))
    if os.environ.get('HA_MQTT_PREFIX'):
        config['behavior']['sensorprefix'] = os.environ.get('HA_MQTT_PREFIX')


def execute(config, get_items, register_callback, do_stop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("HA-MQTT sink plugin disabled")
        return

    logging.info("Starting HA-MQTT sink")

    global mqtt_settings
    mqtt_settings = Settings.MQTT(host=config['server']['address'],
                                  username=config['server']['username'],
                                  password=config['server']['password'],
                                  discovery_prefix=config['behavior']['sensorprefix'])

    # We only publish data on change
    register_callback(my_callback)

    i = 0
    while not do_stop():
        # while we're normally only publishing on change (see callback below), once a minute (default) push out everything
        if i % int(config['behavior']['updatefreq']) == 0:
            # first, retrieve all unique first name-sections from dictionary
            sma_items = get_items()
            unique_parts = set()
            for path in sma_items.keys():
                first_part = path.split('.')[0]
                unique_parts.add(first_part)

            for part in unique_parts:
                # retrieve sub-set of sma_items that contains keys beginning with 'part' (current device)
                filtered_items = {k: v for k, v in sma_items.items() if k.split('.')[0] == part}

                # create device_info objects
                device_info = device_infos.get(part)
                if device_info is None:
                    # create device info if not already in dict
                    device_items = {k: v for k, v in filtered_items.items() if k.split('.')[2] == 'device_info'}
                    # remove the leading parts of each key, just leave the last part
                    di = {k.split(".")[-1]: v for k, v in device_items.items()}
                    device_info = DeviceInfo(name=di['name'],
                                             identifiers=di['identifiers'],
                                             model=di['model'],
                                             manufacturer=di['manufacturer'],
                                             sw_version=di['sw_version'])
                    device_infos[part] = device_info

                for key, value in filtered_items.items():
                    sensor = get_sensor(key, value, device_info)
                    publish(sensor, value)
        i = i+1
        time.sleep(1)

    # Disconnect from the broker
    logging.info("Stopping HA-MQTT sink")


def get_sensor(name, value, device_info):
    global sensors
    sensor = sensors.get(name)
    if (sensor is None):
        # create sensor if not already in dict
        unit = ""
        if isinstance(value, tuple):
            unit = value[1]
        sensor_info = SensorInfo(unit_of_measurement=unit,
                                 name=".".join(name.split(".")[2:]),
                                 device_class=None,
                                 unique_id=name,
                                 device=device_info)
        sensor = Sensor(Settings(mqtt=mqtt_settings, entity=sensor_info))
        sensors[name] = sensor
    return sensor


def publish(sensor, value):
    publish_value = value
    if isinstance(value, tuple):
        publish_value = value[0]
    sensor.set_state(publish_value)


def my_callback(key, value):
    sensor = sensors.get(key)
    if sensor is not None:
        publish(sensor, value)
