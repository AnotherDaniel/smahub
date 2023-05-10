'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''
import logging
import os
import socket
import struct
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

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", MCAST_PORT))
        try:
            mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(IPBIND))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        except BaseException:
            logging.critical("Could not connect to SHM2 multicast socket")
            return

        DeviceInfo = {}
        while not dostop():
            emdata = decode_speedwire(sock.recv(608))
            if (emdata.get("protocol", 0) not in [0x6069] or emdata.get("serial") is None):
                continue

            DeviceInfo['name'] = "SMA Sunny Home Manager 2"
            DeviceInfo['identifiers'] = emdata['serial']
            DeviceInfo['model'] = "EM/SHM/SHM2"
            DeviceInfo['manufacturer'] = "SMA"
            DeviceInfo['sw_version'] = emdata['speedwire-version']

            for key, value in DeviceInfo.items(): 
                dname = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.device_info.{key}"
                add_data(dname, value)

            for key, value in emdata.items():
                if (key.endswith("unit") or key in ["serial", "protocol", "speedwire-version"]):
                    continue

                # a bit elaborate, but stupid is easy to follow in this case - sort things into topic hierarchies
                if "p1" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.p.1.{str(key)}"
                elif "q1" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.q.1.{str(key)}"
                elif "s1" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.s.1.{str(key)}"
                elif "p2" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.p.2.{str(key)}"
                elif "q2" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.q.2.{str(key)}"
                elif "s2" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.s.2.{str(key)}"
                elif "p3" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.p.3.{str(key)}"
                elif "q3" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.q.3.{str(key)}"
                elif "s3" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.s.4.{str(key)}"
                elif key.startswith('p'): 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.p.{str(key)}"
                elif key.startswith('q'): 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.q.{str(key)}"
                elif key.startswith('s'): 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.s.{str(key)}"
                elif "1" in key: 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.1.{str(key)}"
                elif "2" in key: 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.2.{str(key)}"
                elif "3" in key: 
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.3.{str(key)}"
                elif "cosphi" in key or "frequency" in key:
                    ename = f"{config.get('server', 'sensorPrefix')}{DeviceInfo['identifiers']}.{str(key)}"                    
                else:
                    logging.debug(key)
                    continue

                add_data(ename, (value, emdata[f"{key}unit"]))                

    logging.info("Stopping SHM2 source")
