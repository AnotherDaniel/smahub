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

---

## Home Assistant MQTT sensor configuration

This is a list of Home Assistant MQTT sensor definitions to add to `configuration.yaml` (mqtt: section). This makes all data collected by this plugin available in Home Assistant, published via the smahub MQTT sink plugin. This list can be (re)created using the smahub gen_ha_sensors plugin.


```yaml
- name: SHM2_3015975172_device_info_name
  state_topic: "SHM2/3015975172/device_info/name"
  icon: "mdi:camera-switch"
- name: SHM2_3015975172_device_info_identifiers
  state_topic: "SHM2/3015975172/device_info/identifiers"
  icon: "mdi:camera-switch"
- name: SHM2_3015975172_device_info_model
  state_topic: "SHM2/3015975172/device_info/model"
  icon: "mdi:camera-switch"
- name: SHM2_3015975172_device_info_manufacturer
  state_topic: "SHM2/3015975172/device_info/manufacturer"
  icon: "mdi:camera-switch"
- name: SHM2_3015975172_device_info_sw_version
  state_topic: "SHM2/3015975172/device_info/sw_version"
  icon: "mdi:camera-switch"
- name: SHM2_3015975172_p_pconsume
  state_topic: "SHM2/3015975172/p/pconsume"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_pconsumecounter
  state_topic: "SHM2/3015975172/p/pconsumecounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_p_psupply
  state_topic: "SHM2/3015975172/p/psupply"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_psupplycounter
  state_topic: "SHM2/3015975172/p/psupplycounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_q_qconsume
  state_topic: "SHM2/3015975172/q/qconsume"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_qconsumecounter
  state_topic: "SHM2/3015975172/q/qconsumecounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_q_qsupply
  state_topic: "SHM2/3015975172/q/qsupply"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_qsupplycounter
  state_topic: "SHM2/3015975172/q/qsupplycounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_s_sconsume
  state_topic: "SHM2/3015975172/s/sconsume"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_sconsumecounter
  state_topic: "SHM2/3015975172/s/sconsumecounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_s_ssupply
  state_topic: "SHM2/3015975172/s/ssupply"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_ssupplycounter
  state_topic: "SHM2/3015975172/s/ssupplycounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_cosphi
  state_topic: "SHM2/3015975172/cosphi"
  unit_of_measurement: "°"
- name: SHM2_3015975172_frequency
  state_topic: "SHM2/3015975172/frequency"
  unit_of_measurement: "Hz"
  device_class: "frequency"
  state_class: "measurement"
- name: SHM2_3015975172_p_1_p1consume
  state_topic: "SHM2/3015975172/p/1/p1consume"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_1_p1consumecounter
  state_topic: "SHM2/3015975172/p/1/p1consumecounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_p_1_p1supply
  state_topic: "SHM2/3015975172/p/1/p1supply"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_1_p1supplycounter
  state_topic: "SHM2/3015975172/p/1/p1supplycounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_q_1_q1consume
  state_topic: "SHM2/3015975172/q/1/q1consume"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_1_q1consumecounter
  state_topic: "SHM2/3015975172/q/1/q1consumecounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_q_1_q1supply
  state_topic: "SHM2/3015975172/q/1/q1supply"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_1_q1supplycounter
  state_topic: "SHM2/3015975172/q/1/q1supplycounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_s_1_s1consume
  state_topic: "SHM2/3015975172/s/1/s1consume"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_1_s1consumecounter
  state_topic: "SHM2/3015975172/s/1/s1consumecounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_s_1_s1supply
  state_topic: "SHM2/3015975172/s/1/s1supply"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_1_s1supplycounter
  state_topic: "SHM2/3015975172/s/1/s1supplycounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_1_i1
  state_topic: "SHM2/3015975172/1/i1"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: SHM2_3015975172_1_u1
  state_topic: "SHM2/3015975172/1/u1"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: SHM2_3015975172_1_cosphi1
  state_topic: "SHM2/3015975172/1/cosphi1"
  unit_of_measurement: "°"
- name: SHM2_3015975172_p_2_p2consume
  state_topic: "SHM2/3015975172/p/2/p2consume"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_2_p2consumecounter
  state_topic: "SHM2/3015975172/p/2/p2consumecounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_p_2_p2supply
  state_topic: "SHM2/3015975172/p/2/p2supply"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_2_p2supplycounter
  state_topic: "SHM2/3015975172/p/2/p2supplycounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_q_2_q2consume
  state_topic: "SHM2/3015975172/q/2/q2consume"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_2_q2consumecounter
  state_topic: "SHM2/3015975172/q/2/q2consumecounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_q_2_q2supply
  state_topic: "SHM2/3015975172/q/2/q2supply"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_2_q2supplycounter
  state_topic: "SHM2/3015975172/q/2/q2supplycounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_s_2_s2consume
  state_topic: "SHM2/3015975172/s/2/s2consume"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_2_s2consumecounter
  state_topic: "SHM2/3015975172/s/2/s2consumecounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_s_2_s2supply
  state_topic: "SHM2/3015975172/s/2/s2supply"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_2_s2supplycounter
  state_topic: "SHM2/3015975172/s/2/s2supplycounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_2_i2
  state_topic: "SHM2/3015975172/2/i2"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: SHM2_3015975172_2_u2
  state_topic: "SHM2/3015975172/2/u2"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: SHM2_3015975172_2_cosphi2
  state_topic: "SHM2/3015975172/2/cosphi2"
  unit_of_measurement: "°"
- name: SHM2_3015975172_p_3_p3consume
  state_topic: "SHM2/3015975172/p/3/p3consume"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_3_p3consumecounter
  state_topic: "SHM2/3015975172/p/3/p3consumecounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_p_3_p3supply
  state_topic: "SHM2/3015975172/p/3/p3supply"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: SHM2_3015975172_p_3_p3supplycounter
  state_topic: "SHM2/3015975172/p/3/p3supplycounter"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total"
- name: SHM2_3015975172_q_3_q3consume
  state_topic: "SHM2/3015975172/q/3/q3consume"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_3_q3consumecounter
  state_topic: "SHM2/3015975172/q/3/q3consumecounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_q_3_q3supply
  state_topic: "SHM2/3015975172/q/3/q3supply"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: SHM2_3015975172_q_3_q3supplycounter
  state_topic: "SHM2/3015975172/q/3/q3supplycounter"
  unit_of_measurement: "kvarh"
- name: SHM2_3015975172_s_4_s3consume
  state_topic: "SHM2/3015975172/s/4/s3consume"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_4_s3consumecounter
  state_topic: "SHM2/3015975172/s/4/s3consumecounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_s_4_s3supply
  state_topic: "SHM2/3015975172/s/4/s3supply"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: SHM2_3015975172_s_4_s3supplycounter
  state_topic: "SHM2/3015975172/s/4/s3supplycounter"
  unit_of_measurement: "kVAh"
- name: SHM2_3015975172_3_i3
  state_topic: "SHM2/3015975172/3/i3"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: SHM2_3015975172_3_u3
  state_topic: "SHM2/3015975172/3/u3"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: SHM2_3015975172_3_cosphi3
  state_topic: "SHM2/3015975172/3/cosphi3"
  unit_of_measurement: "°"
```