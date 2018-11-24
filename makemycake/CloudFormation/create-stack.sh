#!/bin/bash -ex
SCRIPT_DIR=$(cd -L $(dirname $0) && pwd -L)

# Set variables
STACK_NAME=MakeMyCakeAppStack
TEMPLATE_FILE=$SCRIPT_DIR/MakeMyCake_Template.yml
PARAMETERS_FILE=$SCRIPT_DIR/MakeMyCake_Parameters.json

if aws cloudformation describe-stacks --stack-name $STACK_NAME >/dev/null 2>/dev/null
then
  create_update=update
else
  create_update=create
fi

aws cloudformation ${create_update}-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --parameters file://$PARAMETERS_FILE $@ && \
aws cloudformation wait stack-${create_update}-complete \
  --stack-name $STACK_NAME

echo "=== STACK CREATED/UPDATED SUCCESSFULLY ==="
