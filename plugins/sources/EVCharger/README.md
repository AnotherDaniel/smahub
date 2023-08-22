# SMA EV Carger Source Plugin

The EV Charger source plugin is a SMAHub source plugin that retrieves data from a SMA EV Charger inverter using its built-in HTTP API. The plugin periodically polls the inverter for data and forwards the data to SMAHub for further processing.

## Configuration

The configuration file for the EV Charger source plugin is located in the `config` directory and has the following format:

```ini
[plugin]
enabled = true

[server]
address = 192.168.0.2
username = user
protocol = https
verifyTls = false
password = pwd
updateFreq = 2
sensorPrefix = EV Charger.
```

To enable the EV Charger source plugin, set `enabled` to `true`. Update the `address`, `username`, and `password` fields to match the EV Charger inverter's IP address and credentials. Set the `updateFreq` to the desired update frequency (in seconds). Update the `sensorPrefix` to match the desired prefix for the sensors in the SMAHub.

## Environment Variables

The EV Charger source plugin can also be configured using the following environment variables:

- `EVCHARGER_ENABLED`: Set to `true` to enable the plugin.
- `EVCHARGER_ADDRESS`: The IP address of the EV Charger inverter.
- `EVCHARGER_PROTOCOL`: Communication protocol to use, must be either http or https.
- `EVCHARGER_VERIFYTLS`: Check validity of https (secure) connection, either `true` or `false`.
- `EVCHARGER_USER`: The username for the EV Charger inverter.
- `EVCHARGER_PASSWORD`: The password for the EV Charger inverter.
- `EVCHARGER_UPDATEFREQ`: The update frequency (in seconds).
- `EVCHARGER_PREFIX`: The prefix to use for the sensors in the SMAHub.

## How It Works

The EV Charger source plugin starts by logging into the EV Charger inverter's HTTP API using the provided credentials. Once logged in, the plugin retrieves the device information and stores it.

The plugin then enters a loop where it periodically polls the inverter for data using the `/api/v1/measurements/live` endpoint. The retrieved data is then forwarded to SMAHub using the `add_data` function, which includes the sensor prefix and the sensor key (e.g., `EV Charger.power`). The forwarded data can then be consumed by SMAHub and its sink plugins.

When the plugin is running, you should see the EV Charger data being received and forwarded to SMAHub in the logs.

Note: Ensure that your EV Charger inverter and the SMAHub server are on the same network and that the inverter's HTTP API is accessible.

---

## Home Assistant MQTT sensor configuration

This is a list of Home Assistant MQTT sensor definitions to add to `configuration.yaml` (mqtt: section). This makes all data collected by this plugin available in Home Assistant, published via the smahub MQTT sink plugin. This list can be (re)created using the smahub gen_ha_sensors plugin.
Important: You have to replace "<SERIAL>" with the serial number of the device you are monitoring!

```yaml
- name: EVCHARGER_<SERIAL>_device_info_name
  state_topic: "EVCharger/<SERIAL>/device_info/name"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_device_info_configuration_url
  state_topic: "EVCharger/<SERIAL>/device_info/configuration_url"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_device_info_identifiers
  state_topic: "EVCharger/<SERIAL>/device_info/identifiers"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_device_info_model
  state_topic: "EVCharger/<SERIAL>/device_info/model"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_device_info_manufacturer
  state_topic: "EVCharger/<SERIAL>/device_info/manufacturer"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_device_info_sw_version
  state_topic: "EVCharger/<SERIAL>/device_info/sw_version"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_GridMs_A_phsA
  state_topic: "EVCharger/<SERIAL>/GridMs/A/phsA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_A_phsB
  state_topic: "EVCharger/<SERIAL>/GridMs/A/phsB"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_A_phsC
  state_topic: "EVCharger/<SERIAL>/GridMs/A/phsC"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_Hz
  state_topic: "EVCharger/<SERIAL>/GridMs/Hz"
  unit_of_measurement: "Hz"
  device_class: "frequency"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_PhV_phsA
  state_topic: "EVCharger/<SERIAL>/GridMs/PhV/phsA"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_PhV_phsB
  state_topic: "EVCharger/<SERIAL>/GridMs/PhV/phsB"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_PhV_phsC
  state_topic: "EVCharger/<SERIAL>/GridMs/PhV/phsC"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_PhV_phsC2A
  state_topic: "EVCharger/<SERIAL>/GridMs/PhV/phsC2A"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_TotA
  state_topic: "EVCharger/<SERIAL>/GridMs/TotA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_TotPF
  state_topic: "EVCharger/<SERIAL>/GridMs/TotPF"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_GridMs_TotVA
  state_topic: "EVCharger/<SERIAL>/GridMs/TotVA"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_GridMs_TotVAr
  state_topic: "EVCharger/<SERIAL>/GridMs/TotVAr"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_InOut_GI1
  state_topic: "EVCharger/<SERIAL>/InOut/GI1"
  icon: "mdi:border-all"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotWhIn
  state_topic: "EVCharger/<SERIAL>/Metering/GridMs/TotWhIn"
  unit_of_measurement: "Wh"
  device_class: "energy"
  state_class: "total_increasing"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotWhIn_ChaSta
  state_topic: "EVCharger/<SERIAL>/Metering/GridMs/TotWhIn/ChaSta"
  unit_of_measurement: "Wh"
  device_class: "energy"
  state_class: "total_increasing"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotkWhIn
  state_topic: "EVCharger/<SERIAL>/Metering/GridMs/TotWhIn"
  unit_of_measurement: kWh
  device_class: energy
  state_class: total_increasing
  value_template: "{{ value | multiply(0.001) }}"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotkWhIn_ChaSta
  state_topic: EVCharger/<SERIAL>/Metering/GridMs/TotWhIn/ChaSta"
  unit_of_measurement: kWh
  device_class: energy
  state_class: total_increasing
  value_template: "{{ value | multiply(0.001) }}"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotWIn
  state_topic: "EVCharger/<SERIAL>/Metering/GridMs/TotWIn"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: EVCHARGER_<SERIAL>_Metering_GridMs_TotWIn
  state_topic: "EVCharger/<SERIAL>/Metering/GridMs/TotWIn/ChaSta"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
```
