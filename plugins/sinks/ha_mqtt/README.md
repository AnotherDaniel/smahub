# Home Assistant MQTT Publisher Plugin

The Home Assistant MQTT Publisher Plugin is a SMAHub sink plugin that enables the publishing of SMA device data to a MQTT broker. The data can then be utilized by Home Assistant or any other system that can subscribe to MQTT topics.

## Configuration

The configuration file for the Home Assistant MQTT Publisher plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = false

[server]
address = 192.168.0.1
username = ""
password = ""

[behavior]
# This determines the number of seconds before a full republish of all collected data, even if there's been no value updates
updatefreq = 60
sensorprefix = homeassistant
```

To enable the Home Assistant MQTT Publisher Plugin, set `enabled` to `true`. Under the `[server]` section, provide the MQTT server's `address`, `username`, and `password`. 

The `updatefreq` under the `[behavior]` section determines the frequency (in seconds) at which the plugin republishes all collected data, even if there have been no updates. `sensorprefix` sets the prefix for all sensor topics published to the MQTT broker.

## Environment Variables

The Home Assistant MQTT Publisher plugin can also be configured using the following environment variables:

- `HA_MQTT_ENABLED`: Set to `true` to enable the plugin.
- `HA_MQTT_ADDRESS`: The address of the MQTT server.
- `HA_MQTT_USER`: The username for the MQTT server.
- `HA_MQTT_PASSWORD`: The password for the MQTT server.
- `HA_MQTT_UPDATEFREQ`: The frequency (in seconds) at which the plugin republishes all collected data.
- `HA_MQTT_PREFIX`: The prefix for all sensor topics published to the MQTT broker.

## How It Works

The Home Assistant MQTT Publisher plugin works by subscribing to updates from the SMA data dictionary. When an update is received, the plugin publishes the data to the MQTT server.

The plugin also periodically republishes all data from the SMA data dictionary at the configured frequency. This ensures that even if there have been no updates, the current state of all data is periodically pushed to the MQTT server.

The data is published to MQTT topics with the format `<sensorprefix>/<sma_data_key>`, where `<sensorprefix>` is the configured sensor prefix and `<sma_data_key>` is the SMA data key with periods (.) replaced with slashes (/).

The plugin supports both simple values and tuples in the SMA data dictionary. If a value is a tuple, the first element of the tuple is published as the sensor value, and the second element is published as the unit of measurement.

This plugin enables you to easily integrate your SMA devices with Home Assistant or any other system that supports MQTT, providing real-time access to your device data.