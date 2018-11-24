#!/bin/bash

set -e
set -x

# Setup permissions
umask 0022

mkdir -p /apps/flask/makemycakeapp/log /apps/flask/makemycakeapp/tmp

chown -R flask:flask /apps/flask

find /apps/flask/makemycakeapp -type d -exec chmod o+rx {} +
find /apps/flask/makemycakeapp -type f -exec chmod o+r {} +

chmod o+rx /apps /apps/flask /apps/flask/makemycakeapp
chmod +x /apps/flask/makemycakeapp/bin/*
