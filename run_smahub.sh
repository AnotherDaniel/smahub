#!/bin/sh

cd /opt/smahub
exec /usr/bin/python3 ./src/smahub.py -v > /var/log/smahub 2>&1