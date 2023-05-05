# SHM2 Source Plugin

The SHM2 source plugin is a SMAHub source plugin that receives data from a SMA Sunny Home Manager 2.0 (SHM2) device via multicast. The plugin listens for multicast data sent by the SHM2 and forwards the data to SMAHub for further processing.

## Configuration

The configuration file for the SHM2 source plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = true

[server]
sensorPrefix = SHM2.
```

To enable the SHM2 source plugin, set `enabled` to `true`. Update the `sensorPrefix` to match the desired prefix for the sensors in the SMAHub.

## Environment Variables

The SHM2 source plugin can also be configured using the following environment variables:

- `SHM2_ENABLED`: Set to `true` to enable the plugin.
- `SHM2_PREFIX`: The prefix to use for the sensors in the SMAHub.

## How It Works

The SHM2 source plugin listens for multicast data sent by the SHM2 device on the multicast group `239.12.255.254` and port `9522`. The plugin decodes the received Speedwire packets and extracts the relevant data, such as power consumption, power supply, and grid parameters.

The plugin then forwards the data to SMAHub using the `add_data` function, which includes the sensor prefix and the sensor key (e.g., `SHM2.serial.power`). The forwarded data can then be consumed by SMAHub and its sink plugins.

When the plugin is running, you should see the SHM2 data being received and forwarded to SMAHub in the logs.

Note: Ensure that your SHM2 device and the SMAHub server are on the same network and that multicast traffic is allowed between them.