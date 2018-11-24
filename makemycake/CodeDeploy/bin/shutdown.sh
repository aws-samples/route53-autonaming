#!/bin/bash

set -x

SCRIPTDIR=$(cd -L $(dirname $0) && pwd -L)

source $SCRIPTDIR/setenv.sh

PID=$(ps -ef | grep "$PYTHONEXE /apps/flask/makemycakeapp/makecakeapp.py" | grep -v grep | awk '{ print $2 }' | xargs echo )

echo "Killing PID: '$PID'"
kill $PID

sleep 2
echo "makemycakeapp: Server stopped."

exit 0