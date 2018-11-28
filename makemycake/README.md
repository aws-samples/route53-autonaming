# Application running on EC2 Server

This Flask application runs on an EC2 server.

# Contents

## makecakeapp.py

Contains the code for our flask application.

## self-register.py

Script to register/de-register this application (using IP/port) using Route 53 servicediscovery services


# Running

## Update CloudFormation parameters file

### Edit [CloudFormation/MakeMyCake_Parameters.json](CloudFormation/MakeMyCake_Parameters.json) file using your favourite editor

1. **VPCId**

   VPC in which SecurityGroup, AutoscalingGroup will be created

1. **MakeMyCakeAppEC2SubnetIds**

   SubnetIds in which EC2 instances will be created (must be in the same VPC as above)

1. **EC2KeyPair**

   EC2 Keypair Name so you can login to the EC2 instance if needed

1. **MakeMyCakeAppEC2ImageId**

   AWS Linux 2 AMI Id in your region

1. **SSHAllowFromCIDR**

   SSH Access to EC2 instances will be allowed from this IP Address range

1. **MakeMyCakeAppEC2InstanceType**

   EC2 InstanceType. Default of t2.micro will suffice for this demo

1. **MakeMyCakeAppASGMinSize**

   Minimum number of instances in Autoscaling group

1. **MakeMyCakeAppASGMaxSize**

   Maximum number of instances in Autoscaling group

1. **MakeMyCakeAppASGDesiredCapacity**

   Default number of instances in Autoscaling group. Set it to atleast the number of SubnetIds.



## Execute CloudFormation template

In a bash shell with python and awscli installed, run [CloudFormation/create-stack.sh](CloudFormation/create-stack.sh)

You will see the CloudFormation stack getting created like this:

```
9801abcdef23:makemycake flaskuser$ CloudFormation/create-stack.sh
+++ dirname CloudFormation/create-stack.sh
++ cd -L CloudFormation
++ pwd -L
+ SCRIPT_DIR=/Users/flaskuser/r53autonaming/makemycake/CloudFormation
+ STACK_NAME=MakeMyCakeAppStack
+ TEMPLATE_FILE=/Users/flaskuser/r53autonaming/makemycake/CloudFormation/MakeMyCake_Template.yml
+ PARAMETERS_FILE=/Users/flaskuser/r53autonaming/makemycake/CloudFormation/MakeMyCake_Parameters.json
+ aws cloudformation describe-stacks --stack-name MakeMyCakeAppStack
+ create_update=create
+ aws cloudformation create-stack --capabilities CAPABILITY_NAMED_IAM --stack-name MakeMyCakeAppStack --template-body file:///Users/flaskuser/r53autonaming/makemycake/CloudFormation/MakeMyCake_Template.yml --parameters file:///Users/flaskuser/r53autonaming/makemycake/CloudFormation/MakeMyCake_Parameters.json
{
    "StackId": "arn:aws:cloudformation:us-west-2:387124073467:stack/MakeMyCakeAppStack/20b17570-ea0f-11e8-a031-50a68a2012f2"
}
+ aws cloudformation wait stack-create-complete --stack-name MakeMyCakeAppStack
+ echo '=== STACK CREATED/UPDATED SUCCESSFULLY ==='
=== STACK CREATED/UPDATED SUCCESSFULLY ===
```

You can follow the progress of the stack creation in AWS Console. You will see these resources getting created:

1. MakeMyCakeAppEC2InstanceRole

1. MakeMyCakeAppEC2InstanceProfile

1. MakeMyCakeAppEC2SG

1. MakeMyCakeAppLT

1. MakeMyCakeAppASG

1. MakeMyCakeAppCodeDeploy

1. MakeMyCakeAppCodeDeployASGDeploymentGroup

1. AWSCodeDeployServiceRole


## Kickoff CodeDeploy Deployment

Run [CodeDeploy/zip_and_deploy.sh](CodeDeploy/zip_and_deploy.sh) which will do these steps:

1. Packages application and CodeDeploy scripts into a zip file

1. Uploads the zip package to S3 (creates S3 bucket if it does not exist)

1. Creates a CodeDeploy deployment which will roll out the application to EC2 instances in the Autoscaling group

```
9801abcdef23:makemycake flaskuser$ CodeDeploy/zip_and_deploy.sh
+++ dirname CodeDeploy/zip_and_deploy.sh
++ cd -L CodeDeploy
++ pwd -L
+ SCRIPT_DIR=/Users/flaskuser/r53autonaming/makemycake/CodeDeploy
++ mktemp -d
+ TMPDIR=/var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj
+ trap 'exit 1' HUP INT PIPE QUIT TERM
+ trap 'rm -rf /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj' EXIT
++ aws configure get region
+ REGION=us-west-2
++ aws sts get-caller-identity --query Account --output text
+ ACCOUNTID=387124073467
+ S3BUCKET=codedeploy-bucket-us-west-2-387124073467
+ S3KEY=makemycakeapp.zip
+ CODEDEPLOY_APPLICATION_NAME=MakeMyCakeAppWeb
+ CODEDEPLOY_DEPLOYMENT_GROUP_NAME=MakeMyCakeAppWebASG
+ mkdir -p /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp -p /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/appspec.yml /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp -pR /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/bin /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp -pR /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/hooks /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/../makecakeapp.py /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/../self-register.py /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cp /Users/flaskuser/r53autonaming/makemycake/CodeDeploy/../mc-metadata.json /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy/
+ cd /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/CodeDeploy
+ zip -r /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/makemycakeapp.zip .
  adding: appspec.yml (deflated 63%)
  adding: bin/ (stored 0%)
  adding: bin/setenv.sh (deflated 18%)
  adding: bin/shutdown.sh (deflated 27%)
  adding: bin/startup.sh (deflated 39%)
  adding: hooks/ (stored 0%)
  adding: hooks/create_flask_user.sh (deflated 41%)
  adding: hooks/deregister_from_servicediscovery.sh (deflated 22%)
  adding: hooks/install_dependencies.sh (deflated 27%)
  adding: hooks/register_with_servicediscovery.sh (deflated 22%)
  adding: hooks/set_app_permissions.sh (deflated 57%)
  adding: hooks/start_app.sh (deflated 19%)
  adding: hooks/stop_app.sh (deflated 20%)
  adding: hooks/validate_service.sh (deflated 31%)
  adding: makecakeapp.py (deflated 42%)
  adding: mc-metadata.json (deflated 18%)
  adding: self-register.py (deflated 77%)
+ aws s3 ls s3://codedeploy-bucket-us-west-2-387124073467
+ grep -q NoSuchBucket
+ aws s3 cp /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/makemycakeapp.zip s3://codedeploy-bucket-us-west-2-387124073467/makemycakeapp.zip
upload: ../../../../../../../../var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/makemycakeapp.zip to s3://codedeploy-bucket-us-west-2-387124073467/makemycakeapp.zip
+ aws deploy create-deployment --application-name MakeMyCakeAppWeb --deployment-group-name MakeMyCakeAppWebASG --deployment-config-name CodeDeployDefault.OneAtATime --description 'MakeMyCakeAppWeb deployment' --ignore-application-stop-failures --file-exists-behavior OVERWRITE --s3-location bundleType=zip,bucket=codedeploy-bucket-us-west-2-387124073467,key=makemycakeapp.zip
+ tee /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/dep_id.json
{
    "deploymentId": "d-OQPZJGVGW"
}
+ echo '=== DEPLOYMENT STARTED ==='
=== DEPLOYMENT STARTED ===
++ cat /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj/dep_id.json
++ python -c 'import sys,json; print (json.load(sys.stdin)['\''deploymentId'\''])'
+ aws deploy wait deployment-successful --deployment-id d-OQPZJGVGW
+ echo '=== DEPLOYMENT SUCCESSFUL ==='
=== DEPLOYMENT SUCCESSFUL ===
+ rm -rf /var/folders/nh/y03v2znx5091vlknpz_lbyc4p3r0gc/T/tmp.yrC4APcj
9801abcdef23:makemycake flaskuser$
```

# Notes

## CodeDeploy logs location

On the EC2 instances, you can verify the execution of the register/de-register scripts by looking at the codedeploy deployment logs:

**/opt/codedeploy-agent/deployment-root/deployment-logs/codedeploy-agent-deployments.log**

You will see messages like this:

### De-Registration:
```
[2018-11-22 22:45:55.779] [d-GXTUURIKW]Script - hooks/deregister_from_servicediscovery.sh
[2018-11-22 22:45:55.790] [d-GXTUURIKW][stderr]+ sudo -u flask python /apps/flask/makemycakeapp/self-register.py --action deregister-instance --metadata /apps/flask/makemycakeapp/mc-metadata.json
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]Namespace "makecakeshop" exists
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]deregistering caketypes service and instance Id 54.149.219.109 from namespace_id ns-x2nmu52caz2oagd4
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]service exists
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]Operation status is: SUCCESS
[2018-11-22 22:46:06.205] [d-GXTUURIKW][stdout]Deregistration completed with status: SUCCESS
```

### Registration:
```
[2018-11-22 22:42:47.593] [d-1C1EP1RKW]Script - hooks/register_with_servicediscovery.sh
[2018-11-22 22:42:47.604] [d-1C1EP1RKW][stderr]+ sudo -u flask python /apps/flask/makemycakeapp/self-register.py --action register-instance --metadata /apps/flask/makemycakeapp/mc-metadata.json
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]registering caketypes service and instance Id 54.149.219.109
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]DNS Namespace operation ID gqvzz2e7tywvjbyaxfxr6dhcxbdkounz-jot6n37b
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Namespace ID else loop ns-x2nmu52caz2oagd4 and namespaceStatus SUBMITTED and nsOpID gqvzz2e7tywvjbyaxfxr6dhcxbdkounz-jot6n37b
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]create_private_dns_namespace returned namespace_id ns-x2nmu52caz2oagd4 status SUBMITTED opid gqvzz2e7tywvjbyaxfxr6dhcxbdkounz-jot6n37b
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: PENDING
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Operation status is: SUCCESS
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]create service response {'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '1f5ee82d-eea8-11e8-a97e-23dc81fb2db3', 'HTTPHeaders': {'date': 'Thu, 22 Nov 2018 22:44:08 GMT', 'x-amzn-requestid': '1f5ee82d-eea8-11e8-a97e-23dc81fb2db3', 'content-length': '435', 'content-type': 'application/x-amz-json-1.1', 'connection': 'keep-alive'}}, u'Service': {u'Description': u'Created by HTTP service registry', u'DnsConfig': {u'DnsRecords': [{u'Type': u'A', u'TTL': 100}], u'NamespaceId': u'ns-x2nmu52caz2oagd4', u'RoutingPolicy': u'MULTIVALUE'}, u'CreateDate': datetime.datetime(2018, 11, 22, 22, 44, 8, 331000, tzinfo=tzlocal()), u'CreatorRequestId': u'f9d01f4a-e3e2-48e7-b813-51d466c1f5f3', u'Id': u'srv-mpqa42ueuvmqvb6a', u'Arn': u'arn:aws:servicediscovery:us-west-2:387124073467:service/srv-mpqa42ueuvmqvb6a', u'Name': u'caketypes'}}
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]service_id srv-mpqa42ueuvmqvb6a
[2018-11-22 22:44:18.485] [d-1C1EP1RKW][stdout]Response from register_dns_instance:
[2018-11-22 22:44:18.486] [d-1C1EP1RKW][stdout]{'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '1f6810a6-eea8-11e8-8708-774f70bed8ad', 'HTTPHeaders': {'date': 'Thu, 22 Nov 2018 22:44:08 GMT', 'x-amzn-requestid': '1f6810a6-eea8-11e8-8708-774f70bed8ad', 'content-length': '59', 'content-type': 'application/x-amz-json-1.1', 'connection': 'keep-alive'}}, u'OperationId': u'qs74yqoxelabupneysymkpdcrnbb2dhh-jot6otak'}
[2018-11-22 22:44:18.486] [d-1C1EP1RKW][stdout]Sleeping for 10 seconds
[2018-11-22 22:44:18.486] [d-1C1EP1RKW][stdout]Operation status is: SUCCESS
[2018-11-22 22:44:18.486] [d-1C1EP1RKW][stdout]Registration completed with status: SUCCESS
```

# Testing

We can see the effect of registration by performing a DNS lookup {ServiceName}.{NameSpaceName} from any instance in the VPC.

```
[ec2-user@ip-172-31-25-243 ~]$ nslookup caketypes.makecakeshop
Server:   172.31.0.2
Address:  172.31.0.2#53

Non-authoritative answer:
Name: caketypes.makecakeshop
Address: 54.149.219.109
Name: caketypes.makecakeshop
Address: 54.190.36.104
```

We can also get a response using the DNS name
```
[ec2-user@ip-172-31-25-243 ~]$ curl http://caketypes.makecakeshop:5000
{
  "CakeCrustTypes": [
    "VanillaCrust",
    "ChocolateCrust",
    "StrawberryCrust"
  ]
}
[ec2-user@ip-172-31-25-243 ~]$
```

# Improvements

1. De-register the application from route53 when the instance is shutting down

1. Register the application in route53 when instance is rebooted

1. Implement a health-monitoring cron-job that de-registers the application if it is down

MAINTAINER: Sarma Palli