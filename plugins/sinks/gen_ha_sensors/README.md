# MQTT Sink Plugin

The MQTT sink plugin is a SMAHub sink plugin that publishes SMA data to an MQTT broker. This plugin can be used to send data from SMA devices to an MQTT broker, which can then be consumed by other applications and services.

## Configuration

The configuration file for the MQTT sink plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = true

[server]
address = 192.168.0.1
port = 1883
username = ""
password = ""
updatefreq = 2
```

To enable the MQTT sink plugin, set `enabled` to `true`. Update the `address` and `port` to match the MQTT broker's settings. If the broker requires a username and password, update the `username` and `password` fields accordingly. The `updatefreq` value determines the frequency (in seconds) at which the plugin publishes SMA data to the MQTT broker.

## Environment Variables

The MQTT sink plugin can also be configured using the following environment variables:

- `MQTT_ENABLED`: Set to `true` to enable the plugin.
- `MQTT_ADDRESS`: The address of the MQTT broker.
- `MQTT_PORT`: The port of the MQTT broker.
- `MQTT_UPDATEFREQ`: The frequency (in seconds) at which the plugin publishes SMA data to the MQTT broker.

## How It Works

The MQTT sink plugin connects to the specified MQTT broker and subscribes to SMA data updates. When new data is available, the plugin publishes the data as an MQTT message with a topic derived from the SMA data key. The data key's periods (.) are replaced with slashes (/) to create the MQTT topic.

For example, if the SMA data key is `sma.device1.power`, the MQTT topic will be `sma/device1/power`.

When the plugin is running, you should see the SMA data being published to the MQTT broker at the configured update frequency. You can subscribe to the MQTT topics using any MQTT client to consume the data in real-time.