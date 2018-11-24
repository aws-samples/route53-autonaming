#!/bin/bash -ex
SCRIPT_DIR=$(cd -L $(dirname $0) && pwd -L)

# Create a temporary directory and store its name in a variable ...
TMPDIR=$(mktemp -d)
# Make sure it gets removed even if the script exits abnormally.
trap "exit 1" HUP INT PIPE QUIT TERM
trap "rm -rf $TMPDIR" EXIT

# Set variables
REGION=$(aws configure get region)
ACCOUNTID=$(aws sts get-caller-identity --query 'Account' --output text)
S3BUCKET=codedeploy-bucket-$REGION-$ACCOUNTID
S3KEY=makemycakeapp.zip
CODEDEPLOY_APPLICATION_NAME=MakeMyCakeAppWeb
CODEDEPLOY_DEPLOYMENT_GROUP_NAME=MakeMyCakeAppWebASG

# Create a zip for CodeDeploy deployment
mkdir -p $TMPDIR/CodeDeploy/

cp -p   $SCRIPT_DIR/appspec.yml         $TMPDIR/CodeDeploy/
cp -pR  $SCRIPT_DIR/bin                 $TMPDIR/CodeDeploy/
cp -pR  $SCRIPT_DIR/hooks               $TMPDIR/CodeDeploy/
cp      $SCRIPT_DIR/../makecakeapp.py   $TMPDIR/CodeDeploy/
cp      $SCRIPT_DIR/../self-register.py $TMPDIR/CodeDeploy/
cp      $SCRIPT_DIR/../mc-metadata.json $TMPDIR/CodeDeploy/

cd $TMPDIR/CodeDeploy
zip -r $TMPDIR/makemycakeapp.zip .

# Create S3 bucket if it does not exist
if aws s3 ls s3://$S3BUCKET 2>&1 | grep -q 'NoSuchBucket'
then
  aws s3 mb s3://$S3BUCKET
fi

# Upload to S3 bucket
aws s3 cp $TMPDIR/makemycakeapp.zip s3://$S3BUCKET/$S3KEY

# Start deployment
aws deploy create-deployment \
  --application-name $CODEDEPLOY_APPLICATION_NAME \
  --deployment-group-name $CODEDEPLOY_DEPLOYMENT_GROUP_NAME \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --description "$CODEDEPLOY_APPLICATION_NAME deployment" \
  --ignore-application-stop-failures \
  --file-exists-behavior OVERWRITE \
  --s3-location bundleType=zip,bucket=$S3BUCKET,key=$S3KEY | tee $TMPDIR/dep_id.json

echo "=== DEPLOYMENT STARTED ==="

# Wait for deployemnt to be successful
aws deploy wait deployment-successful \
  --deployment-id $(cat $TMPDIR/dep_id.json|python -c "import sys,json; print (json.load(sys.stdin)['deploymentId'])")

echo "=== DEPLOYMENT SUCCESSFUL ==="
