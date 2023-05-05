# Demo Sink Plugin

The demo sink plugin is a simple example of a SMAHub sink plugin. It listens for updates in the SMA data and prints the current SMA values to the console. This plugin is useful for testing and understanding how the SMAHub plugins work.

## Configuration

The configuration file for the demo sink plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = false
```

To enable the demo sink plugin, set `enabled` to `true`.

## Environment Variables

The demo sink plugin can also be enabled using the environment variable `DEMOSINK_ENABLED`. Set it to `true` to enable the plugin.

## How It Works

The demo sink plugin registers a callback function that is called whenever a SMA value is updated. The plugin also prints the current SMA values to the console every 5 seconds.

When the plugin is enabled, you should see output similar to the following in the console:

```console
Current SMA values:
Key: some_key, Value: some_value
Key: another_key, Value: another_value
...
```

This output indicates that the demo sink plugin is receiving updates from SMAHub and processing the data correctly.