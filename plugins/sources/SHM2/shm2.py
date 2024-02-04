'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import os
import fcntl
import time
import socket
import struct
from utils.speedwiredecoder import decode_speedwire
from utils.smasensors import register_sensor_dict


def env_vars(config):
    if os.environ.get('SHM2_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('SHM2_ENABLED')
    if os.environ.get('SHM2_UPDATEFREQ'):
        config['behavior']['updateFreq'] = os.environ.get('SHM2_UPDATEFREQ')
    if os.environ.get('SHM2_PREFIX'):
        config['behavior']['sensorPrefix'] = os.environ.get('SHM2_PREFIX')


def execute(config, add_data, dostop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("SHM2 plugin disabled")
        return

    logging.info("Starting SHM2 source")
    MCAST_GRP = '239.12.255.254'
    MCAST_PORT = 9522
    IPBIND = '0.0.0.0'

    # register ha sensor definitions
    register_sensor_dict('SENSORS_SHM2', SENSORS_SHM2)

    # set up listening socket for SHM2 data packets
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", MCAST_PORT))
        try:
            mreq = struct.pack("4s4s", socket.inet_aton(
                MCAST_GRP), socket.inet_aton(IPBIND))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        except BaseException:
            logging.critical("Could not connect to SHM2 multicast socket")
            return

        DeviceInfo = {}
        DeviceInfo['name'] = "SMA Sunny Home Manager 2"
        DeviceInfo['model'] = "EM/SHM/SHM2"
        DeviceInfo['manufacturer'] = "SMA"

        while not dostop():
            data = ''
            while True:
                try:
                    chunk = sock.recv(608)
                    if chunk:
                        data = chunk
                except BlockingIOError:
                    break

            emdata = decode_speedwire(data)
            if (emdata.get("protocol", 0) not in [0x6069] or emdata.get("serial") is None):
                continue

            DeviceInfo['identifiers'] = emdata['serial']
            DeviceInfo['sw_version'] = emdata['speedwire-version']

            for key, value in DeviceInfo.items():
                dname = f"{config.get('behavior', 'sensorPrefix')}{
                    DeviceInfo['identifiers']}.device_info.{key}"
                add_data(dname, value)

            for key, value in emdata.items():
                if (key.endswith("unit") or key in ["serial", "protocol", "speedwire-version"]):
                    continue

                # a bit elaborate, but stupid is easy to follow in this case - sort things into topic hierarchies
                if "p1" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.p.1.{str(key)}"
                elif "q1" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.q.1.{str(key)}"
                elif "s1" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.s.1.{str(key)}"
                elif "p2" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.p.2.{str(key)}"
                elif "q2" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.q.2.{str(key)}"
                elif "s2" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.s.2.{str(key)}"
                elif "p3" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.p.3.{str(key)}"
                elif "q3" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.q.3.{str(key)}"
                elif "s3" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.s.3.{str(key)}"
                elif key.startswith('p'):
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.p.{str(key)}"
                elif key.startswith('q'):
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.q.{str(key)}"
                elif key.startswith('s'):
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.s.{str(key)}"
                elif "1" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.1.{str(key)}"
                elif "2" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.2.{str(key)}"
                elif "3" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.3.{str(key)}"
                elif "cosphi" in key or "frequency" in key:
                    ename = f"{config.get('behavior', 'sensorPrefix')}{
                        DeviceInfo['identifiers']}.{str(key)}"
                else:
                    logging.debug(key)
                    continue

                add_data(ename, (value, emdata[f"{key}unit"]))

            time.sleep(int(config.get('behavior', 'updateFreq')))

    logging.info("Stopping SHM2 source")


'''
Home Assistant MQTT autodiscovery sensor definitions for SHM2
'''
SENSORS_SHM2 = [
    # device info
    {
        'key': "device_info.name",
        'enabled': "true",
        'name': "Device name",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.identifiers",
        'enabled': "true",
        'name': "Device serial",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.model",
        'enabled': "true",
        'name': "Device model",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.manufacturer",
        'enabled': "true",
        'name': "Device manufacturer",
        'entity_category': "diagnostic",
    },
    {
        'key': "device_info.sw_version",
        'enabled': "true",
        'name': "Device SW version",
        'entity_category': "diagnostic",
    },
    # global measurements
    {
        'key': "p.pconsume",
        'enabled': "true",
        'name': "Active power consumption",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.pconsumecounter",
        'enabled': "true",
        'name': "Active power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "p.psupply",
        'enabled': "true",
        'name': "Active power supply",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.psupplycounter",
        'enabled': "true",
        'name': "Active power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.qconsume",
        'enabled': "true",
        'name': "Reactive power consumption",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.qconsumecounter",
        'enabled': "true",
        'name': "Reactive power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.qsupply",
        'enabled': "true",
        'name': "Reactive power supply",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.qsupplycounter",
        'enabled': "true",
        'name': "Reactive power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.sconsume",
        'enabled': "true",
        'name': "Apparent power consumption",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.sconsumecounter",
        'enabled': "true",
        'name': "Apparent power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.ssupply",
        'enabled': "true",
        'name': "Apparent power supply",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.ssupplycounter",
        'enabled': "true",
        'name': "Apparent power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "cosphi",
        'enabled': "true",
        'name': "Phase angle cosine",
        'unit_of_measurement': "°",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:cosine-wave",
    },
    {
        'key': "frequency",
        'enabled': "true",
        'name': "Grid frequency",
        'device_class': "frequency",
        'unit_of_measurement': "Hz",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:sine-wave",
    },
    # phase 1 measurements
    {
        'key': "p.1.p1consume",
        'enabled': "false",
        'name': "Phase 1 consumption",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.1.p1consumecounter",
        'enabled': "false",
        'name': "Phase 1 consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "p.1.p1supply",
        'enabled': "false",
        'name': "Phase 1 active power supply",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.1.p1supplycounter",
        'enabled': "false",
        'name': "Phase 1 supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.1.q1consume",
        'enabled': "false",
        'name': "Phase 1 reactive power consumption",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.1.q1consumecounter",
        'enabled': "false",
        'name': "Phase 1 reactive power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.1.q1supply",
        'enabled': "false",
        'name': "Phase 1 reactive power supply",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.1.q1supplycounter",
        'enabled': "false",
        'name': "Phase 1 reactive power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.1.s1consume",
        'enabled': "false",
        'name': "Phase 1 apparent power consumption",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.1.s1consumecounter",
        'enabled': "false",
        'name': "Phase 1 apparent power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.1.s1supply",
        'enabled': "false",
        'name': "Phase 1 apparent power supply",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.1.s1supplycounter",
        'enabled': "false",
        'name': "Phase 1 apparent power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "1.i1",
        'enabled': "false",
        'name': "Phase 1 current",
        'device_class': "current",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:current-ac",
    },
    {
        'key': "1.u1",
        'enabled': "false",
        'name': "Phase 1 potential",
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "1.cosphi1",
        'enabled': "false",
        'name': "Phase 1 angle cosine",
        'unit_of_measurement': "°",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:cosine-wave",
    },
    # phase 2 measurements
    {
        'key': "p.2.p2consume",
        'enabled': "false",
        'name': "Phase 2 consumption",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.2.p2consumecounter",
        'enabled': "false",
        'name': "Phase 2 consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "p.2.p2supply",
        'enabled': "false",
        'name': "Phase 2 active power supply",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.2.p2supplycounter",
        'enabled': "false",
        'name': "Phase 2 supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.2.q2consume",
        'enabled': "false",
        'name': "Phase 2 reactive power consumption",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.2.q2consumecounter",
        'enabled': "false",
        'name': "Phase 2 reactive power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.2.q2supply",
        'enabled': "false",
        'name': "Phase 2 reactive power supply",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.2.q2supplycounter",
        'enabled': "false",
        'name': "Phase 2 reactive power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.2.s2consume",
        'enabled': "false",
        'name': "Phase 2 apparent power consumption",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.2.s2consumecounter",
        'enabled': "false",
        'name': "Phase 2 apparent power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.2.s2supply",
        'enabled': "false",
        'name': "Phase 2 apparent power supply",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.2.s2supplycounter",
        'enabled': "false",
        'name': "Phase 2 apparent power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "2.i2",
        'enabled': "false",
        'name': "Phase 2 current",
        'device_class': "current",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:current-ac",
    },
    {
        'key': "2.u2",
        'enabled': "false",
        'name': "Phase 2 potential",
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "2.cosphi2",
        'enabled': "false",
        'name': "Phase 2 angle cosine",
        'unit_of_measurement': "°",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:cosine-wave",
    },
    # phase 3 measurements
    {
        'key': "p.3.p3consume",
        'enabled': "false",
        'name': "Phase 3 consumption",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.3.p3consumecounter",
        'enabled': "false",
        'name': "Phase 3 consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "p.3.p3supply",
        'enabled': "false",
        'name': "Phase 3 active power supply",
        'device_class': "power",
        'unit_of_measurement': "W",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "p.3.p3supplycounter",
        'enabled': "false",
        'name': "Phase 3 supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kWh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.3.q3consume",
        'enabled': "false",
        'name': "Phase 3 reactive power consumption",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.3.q3consumecounter",
        'enabled': "false",
        'name': "Phase 3 reactive power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "q.3.q3supply",
        'enabled': "false",
        'name': "Phase 3 reactive power supply",
        'device_class': "reactive_power",
        'unit_of_measurement': "VAR",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "q.3.q3supplycounter",
        'enabled': "false",
        'name': "Phase 3 reactive power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.3.s3consume",
        'enabled': "false",
        'name': "Phase 3 apparent power consumption",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.3.s3consumecounter",
        'enabled': "false",
        'name': "Phase 3 apparent power consumption counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "s.3.s3supply",
        'enabled': "false",
        'name': "Phase 3 apparent power supply",
        'device_class': "apparent_power",
        'unit_of_measurement': "VA",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:home-lightning-bolt-outline",
    },
    {
        'key': "s.3.s3supplycounter",
        'enabled': "false",
        'name': "Phase 3 apparent power supply counter",
        'device_class': "energy",
        'unit_of_measurement': "kVAh",
        'state_class': "total_increasing",
        'suggested_display_precision': 2,
        'icon': "mdi:counter",
    },
    {
        'key': "3.i3",
        'enabled': "false",
        'name': "Phase 3 current",
        'device_class': "current",
        'unit_of_measurement': "A",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:current-ac",
    },
    {
        'key': "3.u3",
        'enabled': "false",
        'name': "Phase 3 potential",
        'device_class': "voltage",
        'unit_of_measurement': "V",
        'icon': "mdi:flash-triangle-outline",
        'state_class': "measurement",
        'suggested_display_precision': 2,
    },
    {
        'key': "3.cosphi3",
        'enabled': "false",
        'name': "Phase 3 angle cosine",
        'unit_of_measurement': "°",
        'state_class': "measurement",
        'suggested_display_precision': 2,
        'icon': "mdi:cosine-wave",
    },
]
