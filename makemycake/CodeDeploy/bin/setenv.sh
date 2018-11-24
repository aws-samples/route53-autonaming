#!/bin/bash

NOHUP=/usr/bin/nohup

PYTHONEXE=/usr/bin/python

# get default region from EC2 meta-data
export AWS_DEFAULT_REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | python -c "import sys, json; print json.load(sys.stdin)['region']")
