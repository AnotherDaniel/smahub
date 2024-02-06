# MQTT Sink Plugin

The MQTT sink plugin is a SMAHub sink plugin that publishes SMA data to an MQTT broker. This plugin can be used to send data from SMA devices to an MQTT broker, which can then be consumed by other applications and services.

## Configuration

The configuration file for the MQTT sink plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = true

[server]
address = 192.0.2.1
port = 1883
username = ""
password = ""
# false to disable tls, 1 for tls v1.1, 2 for tls v1.2
tls = false
# disable CA verification
tls_insecure = false

[behavior]
# this determines the number of seconds before a full republish of all collected data, even if there's been no value updates
updatefreq = 60
# whether to include data units in publication (will publish value-unit pairs as a tuple)
publish_units = false
```

To enable the MQTT sink plugin, set `enabled` to `true`. Update the `address` and `port` to match the MQTT broker's settings. If the broker requires a username and password, update the `username` and `password` fields accordingly. The `updatefreq` value determines the frequency (in seconds) at which the plugin publishes SMA data to the MQTT broker.

## Environment Variables

The MQTT sink plugin can also be configured using the following environment variables:

- `MQTT_ENABLED`: Set to `true` to enable the plugin.
- `MQTT_ADDRESS`: The address of the MQTT broker.
- `MQTT_PORT`: The port of the MQTT broker.
- `MQTT_TLS`: `false` to disable TLS, `1` for TLS v1.1, `2` for TLS v1.2
- `MQTT_TLS_INSECURE`: Set to `true` to disable server CA verification
- `MQTT_SSL_CA`: CA certificate file of the server
- `MQTT_SSL_CERT`: Broker certificate file
- `MQTT_SSL_KEY`: Broker key file
- `MQTT_UPDATEFREQ`: The frequency (in seconds) at which the plugin publishes SMA data to the MQTT broker.
- `MQTT_PUBLISHUNITS`: Whether to include data units in publication (will publish value-unit pairs as a tuple)

## How It Works

The MQTT sink plugin connects to the specified MQTT broker and subscribes to SMA data updates. When new data is available, the plugin publishes the data as an MQTT message with a topic derived from the SMA data key. The data key's periods (.) are replaced with slashes (/) to create the MQTT topic.

For example, if the SMA data key is `sma.device1.power`, the MQTT topic will be `sma/device1/power`.

When the plugin is running, you should see the SMA data being published to the MQTT broker at the configured update frequency. You can subscribe to the MQTT topics using any MQTT client to consume the data in real-time.

## Notes on TLS

To enable TLS, set `MQTT_TLS` to 1 (for TLS v1.1) or 2 (for TLS v1.2). The setting `MQTT_TLS_INSECURE` can be set to `true` to disable server CA verification (e.g.  to ignore non-matching broker hostname during testing). Beyond that, `MQTT_SSL_CA` is the server certificate to use for on-connect validation. Optionally `MQTT_SSL_CERT` and `MQTT_SSL_KEY` can be used to pass client certificate/key files for client-server authentication.
