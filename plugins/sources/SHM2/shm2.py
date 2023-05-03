'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import os
import socket
import struct
from utils.smahelpers import unit_of_measurement
from utils.speedwiredecoder import decode_speedwire

def env_vars(config):
    if os.environ.get('SHM2_ENABLED'):
        config['plugin']['enabled'] = os.environ.get('SHM2_ENABLED')
    if os.environ.get('SHM2_PREFIX'):
        config['server']['sensorPrefix'] = os.environ.get('SHM2_PREFIX')

def execute(config, add_data, dostop):
    env_vars(config)

    if config.get('plugin', 'enabled').lower() != 'true':
        logging.info("SHM2 plugin disabled")
        return

    logging.info("Starting SHM2 source")
    MCAST_GRP = '239.12.255.254'
    MCAST_PORT = 9522
    IPBIND = '0.0.0.0'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))
    try:
        mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(IPBIND))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    except BaseException:
        logging.ERROR("Could not connect to SHM2 multicast socket")
        return

    DeviceInfo = {}
    while not dostop():
        emdata = decode_speedwire(sock.recv(608))
        if (emdata.get("protocol", 0) not in [0x6069] or emdata.get("serial") is None):
            continue

        DeviceInfo['name'] = "SMA Sunny Home Manager 2"
        DeviceInfo['identifiers'] = emdata["serial"]
        DeviceInfo['model'] = "EM/SHM/SHM2"
        DeviceInfo['manufacturer'] = "SMA"
        DeviceInfo['sw_version'] = emdata['speedwire-version']

        for key, value in DeviceInfo.items(): 
            dname = config.get('server', 'sensorPrefix') + 'device_info.' + key
            logging.debug(dname+': ' + str(value))
            add_data(dname, value)

        for key, value in emdata.items():
            if (key.endswith("unit") or key in ["serial", "protocol", "speedwire-version"]):
                continue

            if "consume" in key or "supply" in key or key in ["cosphi", "frequency", "i1", "u1", "cosphi1", "i2", "u2", "cosphi2", "i3", "u3", "cosphi3"]:
                ename = config.get('server', 'sensorPrefix') + str(emdata["serial"]) + '.' + str(key)
                add_data(ename, (value, unit_of_measurement(key)))

            else:
                logging.debug(key)
