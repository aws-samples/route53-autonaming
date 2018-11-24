Author: Madhuri Peri
This microservice runs in a ECS container.
It leverages the native integration of ECS with Route53.

Steps to perform to get the code here to build, get image, push image to repo, setup cluster, create service are all listed in detail below:

1. Build your image using the Dockerfile.

2. Get an ECS Cluster up and running using the deploy-cfn.yaml template.
 
3. Use task-definition.json to create your task definition

4. Use AWS Console to create the service. The service registering in Route53 is natively integrated. This means, behind the scenes, below commands are run.

4a.  aws servicediscovery create-private-dns-namespace --name tutorial --vpc vpc-abcd1234 --region <your-region>
4b.  Get operation ID from output of command 4a above.
4c.  aws servicediscovery get-operation --operation-id <Operation ID from command above>
4d.  Get namespace ID from the output of command 4c above.
4e.  aws servicediscovery create-service --name myapplication --dns-config 'NamespaceId="<NamespaceId from command above>",DnsRecords=[{Type="A",TTL="300"}]' --health-check-custom-config FailureThreshold=1 --region <your-region>
4f.  Get service ID from the output of command 4e above.
4g.  Save below content in a JSON file named ecs-service-discovery.json
{
    "cluster": "<Your cluster name>",
    "serviceName": "ecs-example-service-discovery",
    "taskDefinition": "<Your task definition above>",
    "serviceRegistries": [
       {
          "registryArn": "arn:aws:servicediscovery:region:aws_account_id:service/<Your service ID from command 4f above>"
       }
    ],
    "networkConfiguration": {
       "awsvpcConfiguration": {
          "assignPublicIp": "ENABLED",
          "securityGroups": [ "your security group ID" ],
          "subnets": [ "your subnet-id " ]
       }
    },
    "desiredCount": 1
}

4h. aws ecs create-service --cli-input-json file://ecs-service-discovery.json --region <your region>



When your service runs, it will automatically register / deregister the tasks that are dynamically added/stopped into your ECS Cluster.

