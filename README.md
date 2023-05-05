# SMAHub

SMAHub is a flexible and modular solution for collecting data from SMA photovoltaic (PV) products and publishing it to various output channels, such as MQTT. This project is designed with a plugin-based architecture, making it easy to extend and adapt to new data sources and sinks.

## What is SMAHub?

SMAHub is a Python-based daemon that runs plugins to collect data from SMA PV products, such as solar inverters and energy meters. It supports different data sources and output channels through a plugin-based architecture. The primary goal of this project is to provide an easy-to-use, extensible, and robust solution for monitoring and managing SMA PV systems.

## How does SMAHub work?

SMAHub works by periodically polling data from SMA PV products using various protocols and interfaces. The data is then processed and published to one or more output channels, such as an MQTT broker. The plugin-based architecture allows SMAHub to be easily extended with new data sources and sinks, making it a versatile solution for monitoring and managing SMA PV systems.

```ascii
            +-------------+
            |    SMAHub   |
            +------+------+
                  |
      +-------------+--------------+
      |                            |
      v                            v
   +--------+                +--------+
   | Source |                |  Sink  |
   +--------+                +--------+
   | Plugin |                | Plugin |
   +--------+                +--------+
````

This diagram shows the main SMAHub component at the top, which manages data collection and publishing. Below that, you can see the two plugin categories: source plugins on the left and sink plugins on the right. The arrows indicate the flow of data from the source plugins to the main SMAHub component, and then to the sink plugins for publishing.

## Plugins

SMAHub uses a plugin-based architecture, which allows it to support different data sources and sinks. Plugins are organized into two categories: sources and sinks.

### Sources

Source plugins are responsible for collecting data from SMA PV products. These plugins can use various protocols and interfaces to connect to the devices, extract the required information, and pass it to the main SMAHub instance. Some examples of source plugins include:

- SHM2: A plugin for the SMA Sunny Home Manager 2, which collects data over the Speedwire protocol.
- Tripower X: A plugin for SMA Tripower X inverters, which collects data using the inverter's built-in REST API.

### Sinks

Sink plugins are responsible for publishing the collected data to various output channels. These plugins receive data from the main SMAHub instance and send it to the desired output. Some examples of sink plugins include:

- MQTT: A plugin that publishes data to an MQTT broker, making it easily accessible for home automation systems like Home Assistant.

## Docker

SMAHub can be easily deployed using Docker. This ensures a consistent environment across different platforms and simplifies installation and configuration. The provided Dockerfile and `docker-compose.yml` make it easy to build and run SMAHub with just a few commands. To get started with SMAHub using Docker, follow these steps:

1. Clone the SMAHub repository or download the source code.

2. Navigate to the project directory and build the Docker image:

   ```shell
   docker-compose build
   ```

3. Modify the `docker-compose.yml` file to adjust the environment variables for your SMA PV devices and MQTT broker.

4. Start the SMAHub container:

   ```shell
   docker-compose up -d
   ```

The SMAHub container will start and begin collecting data from your SMA PV devices, publishing the data to the configured MQTT broker.

## Improvements

There are several areas where SMAHub can be improved:

- Option for different/separate plugin config file directory: Allow users to specify a separate directory for plugin configuration files, making it easier to manage and organize plugin configurations.
- More robust plugin loading: Improve the plugin loading process to handle errors and edge cases more gracefully.

## Contributors/code sources

SMAHub was inspired by and adapted from the following projects:

- Sven (littleyoda) - [Home-Assistant-Tripower-X-MQTT](https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT)
- Wenger Florian (datenschuft) - [SMA-EM](https://github.com/datenschuft/SMA-EM)

I'd like to thank these contributors for their work and for sharing their code, which has been invaluable in the development of SMAHub.
