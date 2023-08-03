#!/bin/sh

cd /opt/smahub
exec /usr/bin/python3 ./src/smahub.py -v 2>&1 | tee /var/log/smahub