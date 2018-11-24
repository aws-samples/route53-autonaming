#!/bin/bash

set -e
set -x

sudo -u flask python /apps/flask/makemycakeapp/self-register.py \
  --action register-instance \
  --metadata /apps/flask/makemycakeapp/mc-metadata.json
