from flask import Flask, render_template
import socket
import requests
import boto3

app = Flask(__name__)

# session = boto3.session.Session(profile_name='myawsdefault')
# r53client = session.client(service_name="route53",region_name='us-east-1')
# servicediscovery = session.client(service_name="servicediscovery",region_name='us-west-2')
# servicediscovery._endpoint.host = 'https://servicediscovery.us-west-2.amazonaws.com'

r53client = boto3.client(service_name="route53")
servicediscovery = boto3.client(service_name="servicediscovery")
servicediscovery._endpoint.host = 'https://servicediscovery.us-west-2.amazonaws.com'

services = []


@app.route("/ping")
def ping():
    return "", 200


def discover_frosting_api():
    print("Get from r53")


def dbaas_ec2_api():
    print("query from r53")


@app.route("/")
def cakecrusts():
        
    return render_template("index.html", services=services)

def give_details_of_http_service(httpNamespace):
    
    namespaceID = None
    
    print ("Printing details of HTTP namespace for the microservices")
    nsListResp = servicediscovery.list_namespaces()
    print("Service list_namespaces resp id {}".format(nsListResp))
    
    for key in nsListResp['Namespaces']:
        if key['Name'] == httpNamespace:
            print (key)
            namespaceID = key['Id']
            namespaceName = key['Name']
        else:
            print ("Skipping")
            
    # Get the services for this namespace
    listSrvResp = servicediscovery.list_services(Filters=[{
        'Name' : 'NAMESPACE_ID',
        'Condition' : 'EQ',
        'Values' : [namespaceID]
    }])
    print ("List srvResp {}".format(listSrvResp))
    
    for srvKey in listSrvResp['Services']:
        print (srvKey)
    
        listInstResp = servicediscovery.list_instances(ServiceId = srvKey['Id'])
        
        for instKey in  listInstResp['Instances']:
            print ("Instance details {} \n ".format(instKey))
            
            services.append({
                'name': srvKey['Name'],
                'InstanceName' : instKey['Id'],
                'Attributes' : instKey['Attributes']
            })


def give_details_of_dns_service(dnsNamespace):
    print("Printing details of EC2 microservice from cloudmap")
    print ("\n ---- Details on hosted zone ----")

    # Get details of the hosted zone
    domResp = r53client.list_hosted_zones_by_name(DNSName=dnsNamespace)
    hzID = domResp['HostedZones'][0]['Id']
    print("Domain resp id {} {}".format(hzID, domResp['HostedZones'][0]))

    print("\n ---- Details on record sets ----")
    hzDet = r53client.list_resource_record_sets(HostedZoneId=hzID)
    print (hzDet)

    for hzKey in hzDet['ResourceRecordSets']:
        if hzKey['Type'] not in ['NS','SOA']:
            print ("here2\n")
            print(hzKey['Name'], hzKey['ResourceRecords'])
            services.append({
                'name': hzKey['Name'],
                'addr': hzKey['Name']+"local",
                'hosts': hzKey['SetIdentifier'],
                'text': "http://" + hzKey['Name'] + "local"
            })

    print("\n")
    print ("\n services {} \n ".format(services))

if __name__ == "__main__":
    # DNS Namespace
    dnsNamespace = 'cloudmaptestdns13'
    give_details_of_dns_service(dnsNamespace)

    # HTTP Namespace
    httpNamespace = 'cloudmaptestnew'
    give_details_of_http_service(httpNamespace)
    
    app.run(debug=True, host='0.0.0.0',  port=8080)
