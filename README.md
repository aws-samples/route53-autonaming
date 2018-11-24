This repository will move to the github repository eventually. 
This is interim until the repository gets created by the Github administrator

## What is in this repository?

This repository contains: 

1) Reference for registering microservices with Amazon Cloud Map and Amazon Route53 Autonaming API's (register-ms.py)
2) Reference for deregistering microservices with Amazon Cloud Map and Amazon Route53 Autonaming API's 
3) Example microservice that can be deployed into EC2 instance backed by ASG
4) Example microservice that can be deployed as serverless using API Gateway and AWS Lambda
5) Example microservice that can be deployed on Amazon ECS 

Each of these above microservices can make either DNS or HTTP based calls to Cloud Map API's (Calls to register-ms.py)

### Deployment:
1) Deploy the register-ms.py as a lambda in your account.
2) Deploy the deregister-ms.py as a lambda in your account.

### To see example services working:
1) Amazon ECS provides numerous examples of creating clusters and deploying service using container to cluster.
2) Deploy the serverless microservice using your standard deployment practices or using the provided cloudformation template.
3) Deploy the EC2 sample microservice using the provided cloudformation template.

### What you need to see register microservice in action:
1) Run the register-microservice lambda using sample event below:
{
  "Protocol": "DNS",
  "NamespaceName": "cloudmapdnsec2",
  "ServiceName": "ec2instancetest",
  "microservicename": "caketypes",
  "instanceId": "172.26.27.12",
  "port": "5000",
  "vpcId": "vpc-f8616c9d"
}

2) Once you have the lambda deployed and API Gateway URL registered, get the "API Gateway URL" address.

You can register the HTTP Namespace by running lambda using 
{
    "Name": "frostingservice", 
    "NamespaceId": "ns-uhawsi3ivlzmrmcm", 
    "CreatorRequestId": "frost-service-1105", 
    "Description": "Frosting APIG MS"
}

The sample code provided for the container microservice, has the calls that demonstrate how to lookup/discover the data registered by other microservices


### Future open issues:
