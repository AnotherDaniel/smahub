# TripowerX Source Plugin

The TripowerX source plugin is a SMAHub source plugin that retrieves data from a SMA Tripower X inverter using its built-in HTTP API. The plugin periodically polls the inverter for data and forwards the data to SMAHub for further processing.

## Configuration

The configuration file for the TripowerX source plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = true

[server]
address = 192.168.0.2
username = user
password = pwd
updatefreq = 2
sensorPrefix = TriPowerX.
```

To enable the TripowerX source plugin, set `enabled` to `true`. Update the `address`, `username`, and `password` fields to match the Tripower X inverter's IP address and credentials. Set the `updatefreq` to the desired update frequency (in seconds). Update the `sensorPrefix` to match the desired prefix for the sensors in the SMAHub.

## Environment Variables

The TripowerX source plugin can also be configured using the following environment variables:

- `TRIPOWERX_ENABLED`: Set to `true` to enable the plugin.
- `TRIPOWERX_ADDRESS`: The IP address of the Tripower X inverter.
- `TRIPOWERX_USER`: The username for the Tripower X inverter.
- `TRIPOWERX_PASSWORD`: The password for the Tripower X inverter.
- `TRIPOWERX_UPDATEFREQ`: The update frequency (in seconds).
- `TRIPOWERX_PREFIX`: The prefix to use for the sensors in the SMAHub.

## How It Works

The TripowerX source plugin starts by logging into the Tripower X inverter's HTTP API using the provided credentials. Once logged in, the plugin retrieves the device information and stores it.

The plugin then enters a loop where it periodically polls the inverter for data using the `/api/v1/measurements/live` endpoint. The retrieved data is then forwarded to SMAHub using the `add_data` function, which includes the sensor prefix and the sensor key (e.g., `TriPowerX.power`). The forwarded data can then be consumed by SMAHub and its sink plugins.

When the plugin is running, you should see the Tripower X data being received and forwarded to SMAHub in the logs.

Note: Ensure that your Tripower X inverter and the SMAHub server are on the same network and that the inverter's HTTP API is accessible.