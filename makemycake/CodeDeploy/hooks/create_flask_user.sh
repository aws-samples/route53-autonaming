#!/bin/bash

set -e
set -x

if grep -q "^flask:" /etc/group
then
  echo "group already exists"
else
  groupadd flask
fi

if id -u flask >/dev/null 2>/dev/null
then
  echo "user already exists"
else
  mkdir -p /apps
  useradd -s /sbin/nologin -g flask -d /apps/flask flask
fi
