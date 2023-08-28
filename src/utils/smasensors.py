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

def get_sensor_dict(name):
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
    return SENSOR_REGISTRY.get(name, None)
