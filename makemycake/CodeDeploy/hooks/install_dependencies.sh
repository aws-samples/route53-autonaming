#!/bin/bash

set -e
set -x

# install the latest one using pip
yum remove -y awscli

yum install -y python-pip

pip install flask boto3 awscli