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

---

## Home Assistant MQTT sensor configuration

This is a list of Home Assistant MQTT sensor definitions to add to `configuration.yaml` (mqtt: section). This makes all data collected by this plugin available in Home Assistant, published via the smahub MQTT sink plugin. This list can be (re)created using the smahub gen_ha_sensors plugin.

```yaml
- name: TriPowerX_3015842895_device_info_name
  state_topic: "TriPowerX/3015842895/device_info/name"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_device_info_configuration_url
  state_topic: "TriPowerX/3015842895/device_info/configuration_url"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_device_info_identifiers
  state_topic: "TriPowerX/3015842895/device_info/identifiers"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_device_info_model
  state_topic: "TriPowerX/3015842895/device_info/model"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_device_info_manufacturer
  state_topic: "TriPowerX/3015842895/device_info/manufacturer"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_device_info_sw_version
  state_topic: "TriPowerX/3015842895/device_info/sw_version"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Coolsys_Inverter_TmpVal_1
  state_topic: "TriPowerX/3015842895/Coolsys/Inverter/TmpVal/1"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_3015842895_Coolsys_Inverter_TmpVal_2
  state_topic: "TriPowerX/3015842895/Coolsys/Inverter/TmpVal/2"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_3015842895_Coolsys_Inverter_TmpVal_3
  state_topic: "TriPowerX/3015842895/Coolsys/Inverter/TmpVal/3"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_3015842895_DcMs_Amp_1
  state_topic: "TriPowerX/3015842895/DcMs/Amp/1"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Amp_2
  state_topic: "TriPowerX/3015842895/DcMs/Amp/2"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Amp_3
  state_topic: "TriPowerX/3015842895/DcMs/Amp/3"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Vol_1
  state_topic: "TriPowerX/3015842895/DcMs/Vol/1"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Vol_2
  state_topic: "TriPowerX/3015842895/DcMs/Vol/2"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Vol_3
  state_topic: "TriPowerX/3015842895/DcMs/Vol/3"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Watt_1
  state_topic: "TriPowerX/3015842895/DcMs/Watt/1"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Watt_2
  state_topic: "TriPowerX/3015842895/DcMs/Watt/2"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_DcMs_Watt_3
  state_topic: "TriPowerX/3015842895/DcMs/Watt/3"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridGuard_Cntry
  state_topic: "TriPowerX/3015842895/GridGuard/Cntry"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_GridMs_A_phsA
  state_topic: "TriPowerX/3015842895/GridMs/A/phsA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_A_phsB
  state_topic: "TriPowerX/3015842895/GridMs/A/phsB"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_A_phsC
  state_topic: "TriPowerX/3015842895/GridMs/A/phsC"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_Hz
  state_topic: "TriPowerX/3015842895/GridMs/Hz"
  unit_of_measurement: "Hz"
  device_class: "frequency"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsA
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsA"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsA2B
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsA2B"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsB
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsB"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsB2C
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsB2C"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsC
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsC"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_PhV_phsC2A
  state_topic: "TriPowerX/3015842895/GridMs/PhV/phsC2A"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_TotA
  state_topic: "TriPowerX/3015842895/GridMs/TotA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_TotPFEEI
  state_topic: "TriPowerX/3015842895/GridMs/TotPFEEI"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_GridMs_TotPFExt
  state_topic: "TriPowerX/3015842895/GridMs/TotPFExt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_GridMs_TotPFPrc
  state_topic: "TriPowerX/3015842895/GridMs/TotPFPrc"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_GridMs_TotVA
  state_topic: "TriPowerX/3015842895/GridMs/TotVA"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_TotVAr
  state_topic: "TriPowerX/3015842895/GridMs/TotVAr"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_TotW
  state_topic: "TriPowerX/3015842895/GridMs/TotW"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_TotW_Pv
  state_topic: "TriPowerX/3015842895/GridMs/TotW/Pv"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VA_phsA
  state_topic: "TriPowerX/3015842895/GridMs/VA/phsA"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VA_phsB
  state_topic: "TriPowerX/3015842895/GridMs/VA/phsB"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VA_phsC
  state_topic: "TriPowerX/3015842895/GridMs/VA/phsC"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VAr_phsA
  state_topic: "TriPowerX/3015842895/GridMs/VAr/phsA"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VAr_phsB
  state_topic: "TriPowerX/3015842895/GridMs/VAr/phsB"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_VAr_phsC
  state_topic: "TriPowerX/3015842895/GridMs/VAr/phsC"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_W_phsA
  state_topic: "TriPowerX/3015842895/GridMs/W/phsA"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_W_phsB
  state_topic: "TriPowerX/3015842895/GridMs/W/phsB"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_GridMs_W_phsC
  state_topic: "TriPowerX/3015842895/GridMs/W/phsC"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_InOut_GI1
  state_topic: "TriPowerX/3015842895/InOut/GI1"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Inverter_VArModCfg_PFCtlVolCfg_Stt
  state_topic: "TriPowerX/3015842895/Inverter/VArModCfg/PFCtlVolCfg/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Isolation_FltA
  state_topic: "TriPowerX/3015842895/Isolation/FltA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_3015842895_Isolation_LeakRis
  state_topic: "TriPowerX/3015842895/Isolation/LeakRis"
  unit_of_measurement: "kOhm"
- name: TriPowerX_3015842895_Metering_TotFeedTms
  state_topic: "TriPowerX/3015842895/Metering/TotFeedTms"
  unit_of_measurement: "s"
  device_class: "duration"
  state_class: "total_increasing"
- name: TriPowerX_3015842895_Metering_TotOpTms
  state_topic: "TriPowerX/3015842895/Metering/TotOpTms"
  unit_of_measurement: "s"
  device_class: "duration"
  state_class: "total_increasing"
- name: TriPowerX_3015842895_Metering_TotWhOut
  state_topic: "TriPowerX/3015842895/Metering/TotWhOut"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_3015842895_Metering_TotWhOut_Pv
  state_topic: "TriPowerX/3015842895/Metering/TotWhOut/Pv"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_3015842895_Operation_BckStt
  state_topic: "TriPowerX/3015842895/Operation/BckStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_DrtStt
  state_topic: "TriPowerX/3015842895/Operation/DrtStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_Evt_Dsc
  state_topic: "TriPowerX/3015842895/Operation/Evt/Dsc"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_Evt_Msg
  state_topic: "TriPowerX/3015842895/Operation/Evt/Msg"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_EvtCntIstl
  state_topic: "TriPowerX/3015842895/Operation/EvtCntIstl"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_EvtCntUsr
  state_topic: "TriPowerX/3015842895/Operation/EvtCntUsr"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_GriSwCnt
  state_topic: "TriPowerX/3015842895/Operation/GriSwCnt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_GriSwStt
  state_topic: "TriPowerX/3015842895/Operation/GriSwStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_Health
  state_topic: "TriPowerX/3015842895/Operation/Health"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_HealthStt_Alm
  state_topic: "TriPowerX/3015842895/Operation/HealthStt/Alm"
  unit_of_measurement: "W"
  device_class: "power"
- name: TriPowerX_3015842895_Operation_HealthStt_Ok
  state_topic: "TriPowerX/3015842895/Operation/HealthStt/Ok"
  unit_of_measurement: "kW"
  device_class: "power"
- name: TriPowerX_3015842895_Operation_HealthStt_Wrn
  state_topic: "TriPowerX/3015842895/Operation/HealthStt/Wrn"
  unit_of_measurement: "W"
  device_class: "power"
- name: TriPowerX_3015842895_Operation_OpStt
  state_topic: "TriPowerX/3015842895/Operation/OpStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_PvGriConn
  state_topic: "TriPowerX/3015842895/Operation/PvGriConn"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_RstrLokStt
  state_topic: "TriPowerX/3015842895/Operation/RstrLokStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_RunStt
  state_topic: "TriPowerX/3015842895/Operation/RunStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_StandbyStt
  state_topic: "TriPowerX/3015842895/Operation/StandbyStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_VArCtl_VArModAct
  state_topic: "TriPowerX/3015842895/Operation/VArCtl/VArModAct"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_VArCtl_VArModStt
  state_topic: "TriPowerX/3015842895/Operation/VArCtl/VArModStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_WMaxLimSrc
  state_topic: "TriPowerX/3015842895/Operation/WMaxLimSrc"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Operation_WMinLimSrc
  state_topic: "TriPowerX/3015842895/Operation/WMinLimSrc"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_PvGen_PvW
  state_topic: "TriPowerX/3015842895/PvGen/PvW"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_3015842895_PvGen_PvWh
  state_topic: "TriPowerX/3015842895/PvGen/PvWh"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_3015842895_SunSpecSig_SunSpecTx
  state_topic: "TriPowerX/3015842895/SunSpecSig/SunSpecTx"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Upd_Stt
  state_topic: "TriPowerX/3015842895/Upd/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_WebConn_Stt
  state_topic: "TriPowerX/3015842895/WebConn/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Wl_ConnStt
  state_topic: "TriPowerX/3015842895/Wl/ConnStt"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Wl_SigPwr
  state_topic: "TriPowerX/3015842895/Wl/SigPwr"
  unit_of_measurement: "%"
- name: TriPowerX_3015842895_Setpoint_PlantControl_InOut_DigOut
  state_topic: "TriPowerX/3015842895/Setpoint/PlantControl/InOut/DigOut"
  icon: "mdi:border-all"
- name: TriPowerX_3015842895_Setpoint_PlantControl_Inverter_WModCfg_WCtlComCfg_W
  state_topic: "TriPowerX/3015842895/Setpoint/PlantControl/Inverter/WModCfg/WCtlComCfg/W"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "total"
```