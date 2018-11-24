#!/bin/bash

set -x

SCRIPTDIR=$(cd -L $(dirname $0) && pwd -L)

source $SCRIPTDIR/setenv.sh

$NOHUP $PYTHONEXE /apps/flask/makemycakeapp/makecakeapp.py >/apps/flask/makemycakeapp/log/makemycakeapp.log 2>&1 &
echo $! >/apps/flask/makemycakeapp/tmp/makemycakeapp.pid

echo "makemycakeapp: Server started."

exit 0