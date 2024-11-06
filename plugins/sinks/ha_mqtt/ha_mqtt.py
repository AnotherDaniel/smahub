import os
import time
import logging
from collections import defaultdict
import ha_mqtt_discoverable
from ha_mqtt_discoverable import Settings
from ha_mqtt_discoverable.sensors import SensorInfo, Sensor, DeviceInfo
from utils.smasensors import get_sensor_dict
from utils.smahelpers import status_string

# store for all the ha_mqtt sensor objects
sensors = defaultdict(Sensor)
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
        config['behavior']['updatefreq'] = os.environ.get('HA_MQTT_UPDATEFREQ')
    if os.environ.get('HA_MQTT_PREFIX'):
        config['behavior']['sensorprefix'] = os.environ.get('HA_MQTT_PREFIX')


def execute(config, get_items, register_callback, do_stop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("HA-MQTT sink plugin disabled")
        return

    logging.info("Starting HA-MQTT sink")

    # ha_mqtt_discoverable logs stuff at level INFO that really doesn't belong there - turn it off
    module_logger = logging.getLogger(ha_mqtt_discoverable.__name__)
    module_logger.setLevel(logging.WARNING)

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
                                             identifiers=[str(di['identifiers']),],
                                             model=di['model'],
                                             manufacturer=di['manufacturer'],
                                             sw_version=di['sw_version'])
                    device_infos[part] = device_info

                sensor_items = {k: v for k, v in filtered_items.items() if k.split('.')[2] != 'device_info'}
                for key, value in sensor_items.items():
                    sensor = get_sensor(key, device_info)
                    publish(sensor, value)
        i = i+1
        time.sleep(1)

    # Disconnect from the broker
    logging.info("Stopping HA-MQTT sink")


def get_item_by_key(list_of_dicts, target_key):
    return next((item for item in list_of_dicts if item['key'] == target_key and item['enabled'] == "true"), None)


def get_sensor(name, device_info):
    global sensors
    sensor = sensors.get(name)
    if (sensor is None):
        # create sensor if not already in dict
        sensors_dict = f"SENSORS_{name.split('.')[0]}".upper()

        if not get_sensor_dict(sensors_dict) or not isinstance(get_sensor_dict(sensors_dict), list):
            logging.error(f"HA-MQTT sensor definitions for {name.split('.')[0]} not found")
            return None

        key = ".".join(name.split(".")[2:])
        result = get_item_by_key(get_sensor_dict(sensors_dict), key)

        if result is None:
            logging.debug(f"HA-MQTT sensor definition for {key} not found or disabled")
            return None

        sensor_info = SensorInfo(unique_id=name,
                                 name=result.get('name'),
                                 unit_of_measurement=result.get('unit_of_measurement'),
                                 device_class=result.get('device_class'),
                                 state_class=result.get('state_class'),
                                 entity_category=result.get('entity_category'),
                                 suggested_display_precision=result.get('suggested_display_precision'),
                                 icon=result.get('icon'),
                                 device=device_info)
        sensor = Sensor(Settings(mqtt=mqtt_settings, entity=sensor_info))
        sensors[name] = sensor
    return sensor


def publish(sensor, value):
    if sensor is None:
        return

    publish_value = value
    # get rid of unit, in case our value is a value/unit tuple
    if isinstance(value, tuple):
        publish_value = value[0]

    # if there's not unit, we should be able to look-up a string value for the parameter number
    if not sensor._entity.unit_of_measurement and status_string(publish_value):
        publish_value = status_string(publish_value)

    sensor.set_state(publish_value)


def my_callback(key, value):
    # device info data is not explicitly published in ha_mqtt
    if 'device_info' in key:
        return
    sensor = sensors.get(key)
    if sensor is not None:
        publish(sensor, value)
