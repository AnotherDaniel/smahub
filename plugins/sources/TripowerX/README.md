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
protocol = https
verifyTls = false
password = pwd
updateFreq = 2
sensorPrefix = TriPowerX.
```

To enable the TripowerX source plugin, set `enabled` to `true`. Update the `address`, `username`, and `password` fields to match the Tripower X inverter's IP address and credentials. Set the `updateFreq` to the desired update frequency (in seconds). Update the `sensorPrefix` to match the desired prefix for the sensors in the SMAHub.

## Environment Variables

The TripowerX source plugin can also be configured using the following environment variables:

- `TRIPOWERX_ENABLED`: Set to `true` to enable the plugin.
- `TRIPOWERX_ADDRESS`: The IP address of the Tripower X inverter.
- `TRIPOWERX_PROTOCOL`: Communication protocol to use, must be either http or https.
- `TRIPOWERX_VERIFYTLS`: Check validity of https (secure) connection, either `true` or `false`.
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
Important: You have to replace "<SERIAL>" with the serial number of the device you are monitoring!

```yaml
- name: TriPowerX_<SERIAL>_device_info_name
  state_topic: "TriPowerX/<SERIAL>/device_info/name"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_device_info_configuration_url
  state_topic: "TriPowerX/<SERIAL>/device_info/configuration_url"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_device_info_identifiers
  state_topic: "TriPowerX/<SERIAL>/device_info/identifiers"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_device_info_model
  state_topic: "TriPowerX/<SERIAL>/device_info/model"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_device_info_manufacturer
  state_topic: "TriPowerX/<SERIAL>/device_info/manufacturer"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_device_info_sw_version
  state_topic: "TriPowerX/<SERIAL>/device_info/sw_version"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Coolsys_Inverter_TmpVal_1
  state_topic: "TriPowerX/<SERIAL>/Coolsys/Inverter/TmpVal/1"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_<SERIAL>_Coolsys_Inverter_TmpVal_2
  state_topic: "TriPowerX/<SERIAL>/Coolsys/Inverter/TmpVal/2"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_<SERIAL>_Coolsys_Inverter_TmpVal_3
  state_topic: "TriPowerX/<SERIAL>/Coolsys/Inverter/TmpVal/3"
  unit_of_measurement: "°C"
  device_class: "temperature"
- name: TriPowerX_<SERIAL>_DcMs_Amp_1
  state_topic: "TriPowerX/<SERIAL>/DcMs/Amp/1"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Amp_2
  state_topic: "TriPowerX/<SERIAL>/DcMs/Amp/2"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Amp_3
  state_topic: "TriPowerX/<SERIAL>/DcMs/Amp/3"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Vol_1
  state_topic: "TriPowerX/<SERIAL>/DcMs/Vol/1"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Vol_2
  state_topic: "TriPowerX/<SERIAL>/DcMs/Vol/2"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Vol_3
  state_topic: "TriPowerX/<SERIAL>/DcMs/Vol/3"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Watt_1
  state_topic: "TriPowerX/<SERIAL>/DcMs/Watt/1"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Watt_2
  state_topic: "TriPowerX/<SERIAL>/DcMs/Watt/2"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_DcMs_Watt_3
  state_topic: "TriPowerX/<SERIAL>/DcMs/Watt/3"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridGuard_Cntry
  state_topic: "TriPowerX/<SERIAL>/GridGuard/Cntry"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_GridMs_A_phsA
  state_topic: "TriPowerX/<SERIAL>/GridMs/A/phsA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_A_phsB
  state_topic: "TriPowerX/<SERIAL>/GridMs/A/phsB"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_A_phsC
  state_topic: "TriPowerX/<SERIAL>/GridMs/A/phsC"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_Hz
  state_topic: "TriPowerX/<SERIAL>/GridMs/Hz"
  unit_of_measurement: "Hz"
  device_class: "frequency"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsA
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsA"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsA2B
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsA2B"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsB
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsB"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsB2C
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsB2C"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsC
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsC"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_PhV_phsC2A
  state_topic: "TriPowerX/<SERIAL>/GridMs/PhV/phsC2A"
  unit_of_measurement: "V"
  device_class: "voltage"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_TotA
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_TotPFEEI
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotPFEEI"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_GridMs_TotPFExt
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotPFExt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_GridMs_TotPFPrc
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotPFPrc"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_GridMs_TotVA
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotVA"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_TotVAr
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotVAr"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_TotW
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotW"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_TotW_Pv
  state_topic: "TriPowerX/<SERIAL>/GridMs/TotW/Pv"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VA_phsA
  state_topic: "TriPowerX/<SERIAL>/GridMs/VA/phsA"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VA_phsB
  state_topic: "TriPowerX/<SERIAL>/GridMs/VA/phsB"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VA_phsC
  state_topic: "TriPowerX/<SERIAL>/GridMs/VA/phsC"
  unit_of_measurement: "VA"
  device_class: "apparent_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VAr_phsA
  state_topic: "TriPowerX/<SERIAL>/GridMs/VAr/phsA"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VAr_phsB
  state_topic: "TriPowerX/<SERIAL>/GridMs/VAr/phsB"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_VAr_phsC
  state_topic: "TriPowerX/<SERIAL>/GridMs/VAr/phsC"
  unit_of_measurement: "var"
  device_class: "reactive_power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_W_phsA
  state_topic: "TriPowerX/<SERIAL>/GridMs/W/phsA"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_W_phsB
  state_topic: "TriPowerX/<SERIAL>/GridMs/W/phsB"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_GridMs_W_phsC
  state_topic: "TriPowerX/<SERIAL>/GridMs/W/phsC"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_InOut_GI1
  state_topic: "TriPowerX/<SERIAL>/InOut/GI1"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Inverter_VArModCfg_PFCtlVolCfg_Stt
  state_topic: "TriPowerX/<SERIAL>/Inverter/VArModCfg/PFCtlVolCfg/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Isolation_FltA
  state_topic: "TriPowerX/<SERIAL>/Isolation/FltA"
  unit_of_measurement: "A"
  device_class: "current"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_Isolation_LeakRis
  state_topic: "TriPowerX/<SERIAL>/Isolation/LeakRis"
  unit_of_measurement: "kOhm"
- name: TriPowerX_<SERIAL>_Metering_TotFeedTms
  state_topic: "TriPowerX/<SERIAL>/Metering/TotFeedTms"
  unit_of_measurement: "s"
  device_class: "duration"
  state_class: "total_increasing"
- name: TriPowerX_<SERIAL>_Metering_TotOpTms
  state_topic: "TriPowerX/<SERIAL>/Metering/TotOpTms"
  unit_of_measurement: "s"
  device_class: "duration"
  state_class: "total_increasing"
- name: TriPowerX_<SERIAL>_Metering_TotWhOut
  state_topic: "TriPowerX/<SERIAL>/Metering/TotWhOut"
  unit_of_measurement: "Wh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_<SERIAL>_Metering_TotWhOut_Pv
  state_topic: "TriPowerX/<SERIAL>/Metering/TotWhOut/Pv"
  unit_of_measurement: "Wh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_<SERIAL>_Operation_BckStt
  state_topic: "TriPowerX/<SERIAL>/Operation/BckStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_DrtStt
  state_topic: "TriPowerX/<SERIAL>/Operation/DrtStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_Evt_Dsc
  state_topic: "TriPowerX/<SERIAL>/Operation/Evt/Dsc"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_Evt_Msg
  state_topic: "TriPowerX/<SERIAL>/Operation/Evt/Msg"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_EvtCntIstl
  state_topic: "TriPowerX/<SERIAL>/Operation/EvtCntIstl"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_EvtCntUsr
  state_topic: "TriPowerX/<SERIAL>/Operation/EvtCntUsr"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_GriSwCnt
  state_topic: "TriPowerX/<SERIAL>/Operation/GriSwCnt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_GriSwStt
  state_topic: "TriPowerX/<SERIAL>/Operation/GriSwStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_Health
  state_topic: "TriPowerX/<SERIAL>/Operation/Health"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_HealthStt_Alm
  state_topic: "TriPowerX/<SERIAL>/Operation/HealthStt/Alm"
  unit_of_measurement: "W"
  device_class: "power"
- name: TriPowerX_<SERIAL>_Operation_HealthStt_Ok
  state_topic: "TriPowerX/<SERIAL>/Operation/HealthStt/Ok"
  unit_of_measurement: "kW"
  device_class: "power"
- name: TriPowerX_<SERIAL>_Operation_HealthStt_Wrn
  state_topic: "TriPowerX/<SERIAL>/Operation/HealthStt/Wrn"
  unit_of_measurement: "W"
  device_class: "power"
- name: TriPowerX_<SERIAL>_Operation_OpStt
  state_topic: "TriPowerX/<SERIAL>/Operation/OpStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_PvGriConn
  state_topic: "TriPowerX/<SERIAL>/Operation/PvGriConn"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_RstrLokStt
  state_topic: "TriPowerX/<SERIAL>/Operation/RstrLokStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_RunStt
  state_topic: "TriPowerX/<SERIAL>/Operation/RunStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_StandbyStt
  state_topic: "TriPowerX/<SERIAL>/Operation/StandbyStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_VArCtl_VArModAct
  state_topic: "TriPowerX/<SERIAL>/Operation/VArCtl/VArModAct"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_VArCtl_VArModStt
  state_topic: "TriPowerX/<SERIAL>/Operation/VArCtl/VArModStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_WMaxLimSrc
  state_topic: "TriPowerX/<SERIAL>/Operation/WMaxLimSrc"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Operation_WMinLimSrc
  state_topic: "TriPowerX/<SERIAL>/Operation/WMinLimSrc"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_PvGen_PvW
  state_topic: "TriPowerX/<SERIAL>/PvGen/PvW"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "measurement"
- name: TriPowerX_<SERIAL>_PvGen_PvWh
  state_topic: "TriPowerX/<SERIAL>/PvGen/PvWh"
  unit_of_measurement: "kWh"
  device_class: "energy"
  state_class: "total_increasing"
- name: TriPowerX_<SERIAL>_SunSpecSig_SunSpecTx
  state_topic: "TriPowerX/<SERIAL>/SunSpecSig/SunSpecTx"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Upd_Stt
  state_topic: "TriPowerX/<SERIAL>/Upd/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_WebConn_Stt
  state_topic: "TriPowerX/<SERIAL>/WebConn/Stt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Wl_ConnStt
  state_topic: "TriPowerX/<SERIAL>/Wl/ConnStt"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Wl_SigPwr
  state_topic: "TriPowerX/<SERIAL>/Wl/SigPwr"
  unit_of_measurement: "%"
- name: TriPowerX_<SERIAL>_Setpoint_PlantControl_InOut_DigOut
  state_topic: "TriPowerX/<SERIAL>/Setpoint/PlantControl/InOut/DigOut"
  icon: "mdi:border-all"
- name: TriPowerX_<SERIAL>_Setpoint_PlantControl_Inverter_WModCfg_WCtlComCfg_W
  state_topic: "TriPowerX/<SERIAL>/Setpoint/PlantControl/Inverter/WModCfg/WCtlComCfg/W"
  unit_of_measurement: "W"
  device_class: "power"
  state_class: "total"
```
