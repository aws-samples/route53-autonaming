# Frosting Micro Service
This is a serverless service powered by a Lambda Function and fronted by API 
Gateway

The Lambda function is written in Python 3.6. The code is included as 
`frosting_ms.py` but is packaged/deployed as inline text in the CloudFormation 
template `frosting.json` 
### Creating the CloudFormation stack
The stack can be created with an awscli command:
```bash
aws cloudformation create-stack \
    --capabilities CAPABILITY_NAMED_IAM \
    --stack-name frosting \
    --template-body "$(cat frosting/frosting.json)"
```

* get the api gateway url (to be used as input to later commands)
```bash
aws --output text cloudformation describe-stacks \
    --stack-name frosting \
    --query 'Stacks[].Outputs[].OutputValue'
```

### Register the Service Instance with Route 53

#### Invoke Register Lambda Function
```bash
aws lambda invoke \
    --fucntion-name register-microservice \
    --payload "{
    \"NamespaceName\": \"frosting\",
    \"ServiceName\": \"frosting\",
    \"Protocol\": \"HTTP\",
    \"port\": \"80\",
    \"apiGatewayUrl\": \"[api gateway url from previous command]\" \
    /tmp/lambda_output.txt
}"
```


#### AWS CLI Commands for reference

##### CreateHttpNamespace
```bash
aws servicediscovery create-http-namespace \
    --name frosting
```

##### CreateService
* get the namespace id
```bash
aws --output text servicediscovery list-namespaces \
    --query 'Namespaces[?Name == `frosting`] | [].Id'
```
* create the service
```bash
aws servicediscovery create-service \
    --name frosting \
    --namespace-id [namespace id from previous command]
```

##### RegisterInstance
* get the service id
```bash
aws --output text servicediscovery list-services \
    --query 'Services[?Name == `frosting`] | [].Id'
```
* register instance
```bash
aws servicediscovery register-instance \
    --service-id [service id from previous command] \
    --instance-id inst-01 \
    --attributes "AWS_INSTANCE_CNAME=[api gateway url from previous command]" 
```


