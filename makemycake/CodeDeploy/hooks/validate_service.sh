#!/bin/bash

set -e
set -x

for i in $(seq 1 10)
do
  if /usr/bin/curl -s http://localhost:5000/ >/dev/null
  then
    echo "Successfully pulled root page."
    exit 0
  fi
  echo "Attempt to curl endpoint returned $?. Backing off and retrying."
  sleep 10
done
echo "Server did not come up after expected time. Failing."
exit 1
