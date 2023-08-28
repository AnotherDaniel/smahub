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
   +--------+                  +--------+
   | Source |                  |  Sink  |
   +--------+                  +--------+
   | Plugin |                  | Plugin |
   +--------+                  +--------+
````

This diagram shows the main SMAHub component at the top, which manages data collection and publishing. Below that, you can see the two plugin categories: source plugins on the left and sink plugins on the right. The arrows indicate the flow of data from the source plugins to the main SMAHub component, and then to the sink plugins for publishing.

## Plugins

SMAHub uses a plugin-based architecture, which allows it to support different data sources and sinks. Plugins are organized into two categories: sources and sinks.

### Sources

Source plugins are responsible for collecting data from SMA PV products. These plugins can use various protocols and interfaces to connect to the devices, extract the required information, and pass it to the main SMAHub instance. Some examples of source plugins include:

- SHM2: A plugin for the SMA Sunny Home Manager 2, which collects data over the Speedwire protocol.
- Tripower X: A plugin for SMA Tripower X inverters, which collects data using the inverter's built-in HTTP API.

### Sinks

Sink plugins are responsible for publishing the collected data to various output channels. These plugins receive data from the main SMAHub instance and send it to the desired output. Some examples of sink plugins include:

- MQTT: A plugin that publishes data to an MQTT broker, making it easily accessible for home automation systems like Home Assistant.
- HA-MQTT: A plugin that uses home assistant libraries to publish data directly into home assistant according to ha mqtt sensor semantics
- gen_ha_sensors: A plugin that generates MQTT sensor definitions of all collected data, for use in Home Assistant configuration.

## Python

To run smahub directly from the command line, you need git, a python interpreter version 3.8 or above, the pip package manager and (suggested) python venv. To install these requirements on an Ubuntu machine, run the following command:

```shell
sudo apt install git python3 python3-pip python3-venv
````

Then, get the code from github:

```shell
git clone https://github.com/AnotherDaniel/smahub.git
```

This will create a directory `smahub` an download the sources from github. Next, enter the project directory and install the project requirements using pip:

At this point it is recommended to set up a little virtual environment for this python project, to avoid conflicts and overlaps between smahub python dependencies with the rest of the system. To this end, change into the program directory and create and activate a "venv":

```shell
cd smahub
python3 -m venv .venv
source .venv/bin/activate
```

Having this prepared, we tell pip to install the project dependencies:

```shell
pip3 install .
```

It should now be possible to run smahub from the command line like this (from the project root directory):

```shell
python3 src/smahub.py --version
```

This should print program name and version, and exit. For more command line options, run smahub with the `--help` argument.

The program test cases can be run with:

```shell
pytest tests
```

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
If you are running SMAHub to publish data to Home Assistant, note that it makes sense to include the SMAHub docker-compose configuration in the docker-compose.yml you're using for Home Assistant, and make it `depend_on` the MQTT broker container so that the broker is available before SMAHub starts. This way, SMAHub will always be started/restarted in conjunction with your Home Assistant instance, making the overall system more robust against reboots etc.

Note: the `docker-compose.yml` file provided in this project is set up to build the smahub container from the repository. You can also directly pull a ready-made smahub container for amd64 or arm64 from github container registry, using something like the following configuration:

```yaml
version: '3'
services:
  smahub:
    image: ghcr.io/anotherdaniel/smahub:latest
    container_name: smahub
    network_mode: host
    restart: unless-stopped
# useful if you manage the MQTT broker from this same docker-compose file
#    depends_on:
#      - mosquitto
    environment:
      -  SMAHUB_VERBOSE=true
      -  TRIPOWERX_ENABLED=true
      -  TRIPOWERX_ADDRESS=192.168.0.1
      -  TRIPOWERX_USER=user
      -  TRIPOWERX_PASSWORD=password
      -  TRIPOWERX_PROTOCOL=https
      -  TRIPOWERX_VERIFYTLS=false
      -  MQTT_ENABLED=false
      -  MQTT_ADDRESS=192.168.0.2
      -  MQTT_PORT=1883
      -  MQTT_USER=user
      -  MQTT_PASSWORD=password
      -  SHM2_ENABLED=true
      -  GENHASENSORS_ENABLED=false
      -  GENHASENSORS_GENERATEFREQ=600
      -  GENHASENSORS_FILEPREFIX=hasensors_
      -  GENHASENSORS_SHM2=mdi:camera-switch
      -  GENHASENSORS_TRIPOWERX=mdi:border-all
      -  HA_MQTT_ENABLED=true
      -  HA_MQTT_ADDRESS=192.168.0.3
```

## Improvements

There are several areas where SMAHub can be improved:

- Option for different/separate plugin config file directory: Allow users to specify a separate directory for plugin configuration files, making it easier to manage and organize plugin configurations
- More robust plugin loading: Improve the plugin loading process to handle errors and edge cases more gracefully
- Extend test cases

## Contributors/code sources

SMAHub was inspired by and adapted from the following projects:

- Sven (littleyoda) - [Home-Assistant-Tripower-X-MQTT](https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT)
- Wenger Florian (datenschuft) - [SMA-EM](https://github.com/datenschuft/SMA-EM)

I'd like to thank these authors for their work and for sharing their code, which has been invaluable in the development of SMAHub. Contributors to the smahub codebase are listed in CONTRIBUTORS.md
