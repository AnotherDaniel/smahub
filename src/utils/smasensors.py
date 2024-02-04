'''
Home Assistant MQTT autodiscovery sensor definition registry for SMA devices
'''

SENSOR_REGISTRY = {}


def register_sensor_dict(device, sensor_info):
    """
    Register a sensor dictionary by associating its name with its corresponding attributes.

    Parameters:
    - name (str): The name used to identify the device.
    - sensor_dict (dict): A dictionary containing the device's sensor attributes.

    Returns:
    None

    Example:
    >>> register_sensors('SENSORS_TRIPOWERX', {'key': 'value'})
    """
    if device not in SENSOR_REGISTRY:
        SENSOR_REGISTRY[device] = sensor_info


def get_sensor_dict(device):
    """
    Retrieve a dictionary of device sensor attributes.

    Parameters:
    - name (str): The name of the device to retrieve sensor data for.

    Returns:
    dict: A dictionary containing the sensor's attributes if found, else None.

    Example:
    >>> get_sensors('SENSORS_TRIPOWERX')
    {'key': 'value'}
    """
    return SENSOR_REGISTRY.get(device, None)


def get_parameter_unit(device_name, target_key):
    """
    Retrieve the unit_of_measurement of a particular key in a device's sensor list.

    Parameters:
    - device_name (str): The name of the device (e.g., 'SENSORS_TRIPOWERX').
    - target_key (str): The target key to look for in the sensor dictionaries (e.g., 'Operation.HealthStt.Alm').

    Returns:
    str or None: The unit_of_measurement if found, else None.
    """
    sensor_list = SENSOR_REGISTRY.get(device_name, [])
    for sensor_dict in sensor_list:
        if sensor_dict['key'] == target_key:
            return sensor_dict.get('unit_of_measurement', None)
    return None
