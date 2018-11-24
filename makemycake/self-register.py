#!/usr/bin/env python

# Script to register/de-register instance with servicediscovery

import datetime
import json
import time
import argparse
from botocore.vendored import requests
import boto3

# Find region from metadata service
DOCUMENT = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
REGION = json.loads(DOCUMENT.text)['region']

CLIENT = boto3.client('servicediscovery', region_name=REGION)

"""
    register a micro service
"""


def get_namespace_id(namespace_name):
    """
    list namespaces
    :param namespace_name:
    :return:
    """
    list_ns_resp = CLIENT.list_namespaces()
    try:
        for ns_key in list_ns_resp.get('Namespaces'):
            if ns_key.get('Name') == namespace_name:
                print('Namespace "{}" exists'.format(namespace_name))
                return ns_key.get('Id')
    except Exception as excpt:
        print(excpt)
        raise
    return None


def get_service_id(namespace_id, service_name):
    """
    list services
    :param service_name:
    :return:
    """
    list_svc_resp = CLIENT.list_services(
        Filters=[{
            'Name': 'NAMESPACE_ID',
            'Values': [namespace_id],
            'Condition': 'EQ'
        }]
    )
    try:
        for svc_key in list_svc_resp.get('Services'):
            if svc_key.get('Name') == service_name:
                print('service exists')
                return svc_key.get('Id')
    except Exception as excpt:
        print(excpt)
        raise
    return None


def create_http_namespace(namespace_name):
    """
    Create HTTP Namespace
    :param namespace_name:
    :return:
    """
    namespace_id = None
    namespace_status = None
    op_id = None
    # Create namespace
    ns_resp = CLIENT.create_http_namespace(
        Name=namespace_name,
        Description='HTTP Namespace created from register service')
    ns_op_id = ns_resp.get('OperationId')
    print('HTTP Namespace operation ID {}'.format(ns_op_id))
    # Get namespace ID
    get_op_id_resp = CLIENT.get_operation(OperationId=ns_op_id)
    namespace_id = get_op_id_resp.get('Operation').get('Targets').get(
        'NAMESPACE')
    namespace_status = get_op_id_resp.get('Operation').get('Status')
    op_id = ns_op_id
    print('Namespace ID else loop {}, operation response {} and operation Id {}'.format(namespace_id, get_op_id_resp, op_id))
    return namespace_id, namespace_status, op_id


def create_private_dns_namespace(namespace_name, vpc_id):
    """
    Create Private DNS Namespace
    :param namespace_name:
    :param vpc_id:
    :return:
    """
    namespace_id = None
    namespace_status = None
    ns_op_id = None
    # Create namespace
    ns_resp = CLIENT.create_private_dns_namespace(
        Name=namespace_name,
        Description='DNS Namespace created from register service',
        Vpc=vpc_id)
    ns_op_id = ns_resp.get('OperationId')
    print('DNS Namespace operation ID {}'.format(ns_op_id))
    # Get namespace ID
    get_op_id_resp = CLIENT.get_operation(OperationId=ns_op_id)
    namespace_id = get_op_id_resp.get('Operation').get('Targets').get(
        'NAMESPACE')
    namespace_status = get_op_id_resp.get('Operation').get('Status')
    print('Namespace ID else loop {} and namespaceStatus {} and nsOpID {}'.
          format(namespace_id, namespace_status, ns_op_id))

    return namespace_id, namespace_status, ns_op_id


def create_service(namespace_id, service_name):
    """
    Create Service
    :param namespace_id:
    :param service_name:
    :return:
    """
    try:
        create_srv_resp = CLIENT.create_service(
            Name=service_name,
            Description='Created by HTTP service registry',
            DnsConfig={
                'NamespaceId': namespace_id,
                'RoutingPolicy': 'MULTIVALUE',
                'DnsRecords': [
                    {
                        'Type': 'A',
                        'TTL': 100
                    },
                ]
            }
        )
        print('create service response {}'.format(create_srv_resp))
        service_id = create_srv_resp.get('Service').get('Id')
        print('service_id {}'.format(service_id))
        return service_id
    except CLIENT.exceptions.ServiceAlreadyExists:
        print('ServiceAlreadyExists')
        return get_service_id(namespace_id, service_name)
    return None


def create_http_service(namespace_id, service_name):
    """
    Create HTTP Service
    :param namespace_id:
    :param service_name:
    :return:
    """
    # Create service
    try:
        create_srv_resp = CLIENT.create_service(
            Name=service_name, NamespaceId=namespace_id)
        print('Create HTTP Service response {}'.format(create_srv_resp))
        service_id = create_srv_resp.get('Service').get('Id')
        print('HTTP Service ID {}'.format(service_id))
    except CLIENT.exceptions.ServiceAlreadyExists:
        print('ServiceAlreadyExists')
        return get_service_id(namespace_id, service_name)
    return None


def register_http_instance(api_gateway_url, service_id):
    """
    Register HTTP Instance
    :param api_gateway_url:
    :param service_id:
    :return:
    """
    try:
        reg_inst_resp = CLIENT.register_instance(
            ServiceId=service_id,
            Attributes={'AWS_INSTANCE_CNAME': api_gateway_url},
            InstanceId='inst-01')
        reg_inst_op_id = reg_inst_resp.get('OperationId')
        get_reg_inst_ops_resp = CLIENT.get_operation(
            OperationId=reg_inst_op_id)
        print('get_reg_inst_ops_resp {}'.format(get_reg_inst_ops_resp))
        print('Register instance response {}'.format(reg_inst_resp))
    except Exception as excpt:
        print(excpt)
        print('Error while registering the instance')
        raise

def register_dns_instance(service_id, instance_ip, port):
    """
    Register DNS Instance
    :param service_id:
    :param instance_ip:
    :param port:
    :return:
    """
    # Instance ID for a DNS service discovery would be a IP address and port
    # if ECS container service - A/SRV record
    # TODO: Need to get these from the EC2 instance that is invoking this
    # We don't expect this would be invoked by ECS, as it is natively integrated
    timestamp = datetime.datetime.now()
    creator_request_id = 'register_dns_instance {}'.format(timestamp)
    # Register instance for DNS endpoint (Compute on EC2)
    response = CLIENT.register_instance(
        ServiceId=service_id,
        InstanceId=instance_ip,
        CreatorRequestId=creator_request_id,
        Attributes={
            'AWS_INSTANCE_IPV4': instance_ip,
            'AWS_INSTANCE_PORT': port
        })
    print('Response from register_dns_instance:\n{}'.format(response))
    status = get_operation_status(response['OperationId'])
    while status not in ('SUCCESS', 'FAILED', 'FAIL'):
        print('Sleeping for 10 seconds')
        time.sleep(10)
        status = get_operation_status(response['OperationId'])
        print("Operation status is: {}".format(status))
    print("Registration completed with status: {}".format(status))


def get_operation_status(op_id):
    """
    get operation status
    :param op_id:
    :return:
    """
    get_ops_resp = CLIENT.get_operation(OperationId=op_id)
    op_status = get_ops_resp.get('Operation').get('Status')
    return op_status


def register(namespace_name, service_name,  # pylint: disable=R0913
             protocol, instance_ip, port,
             api_gateway_url, vpc_id):
    """
    perform registration action with Route 53 for DNS based microservice.
    These are the EC2 and ECS microservices. ECS has native integration, so it
    will not invoke this.
    :return:
    """
    print('registering {} service and instance Id {}'.format(
        service_name, instance_ip))

    # Check if the namespace exists, if not create it
    # Get/Create HTTP namespace ID
    namespace_id = get_namespace_id(namespace_name)
    if namespace_id is None and protocol == 'HTTP':
        namespace_id, namespace_status, op_id = create_http_namespace(
            namespace_name)
        print(
            'create_http_namespace returned namespace_id {} status {}'.format(
                namespace_id, namespace_status))
        # TODO: Could be improved in future.
        # Just sleep and check after 2 minutes.
        while namespace_status not in ('SUCCESS', 'FAILED', 'FAIL'):
            print('Sleeping 2 minutes')
            time.sleep(120)
            namespace_status = get_operation_status(op_id)
            # Namespace is now successful
    elif namespace_id is None and protocol == 'DNS':
        namespace_id, namespace_status, op_id = create_private_dns_namespace(
            namespace_name, vpc_id)
        print('create_private_dns_namespace returned namespace_id '
              '{} status {} opid {}'.format(namespace_id, namespace_status,
                                            op_id))
        while namespace_status not in ('SUCCESS', 'FAILED', 'FAIL'):
            print('Sleeping for 10 seconds')
            time.sleep(10)
            namespace_status = get_operation_status(op_id)
            print("Operation status is: {}".format(namespace_status))
            # Namespace is now successful
    if protocol == 'HTTP' and namespace_id is not None:
        # No need to create service
        service_id = create_http_service(namespace_id, service_name)
        register_http_instance(api_gateway_url, service_id)
    elif protocol == 'DNS' and namespace_id is not None:
        # Create the service
        service_id = create_service(namespace_id, service_name)
        # Register instance
        register_dns_instance(service_id, instance_ip, port)


def deregister(namespace_name, service_name, instance_ip):  # pylint: disable=R0913
    """
    perform deregistration action with Route 53 for DNS based microservice.
    These are the EC2 and ECS microservices. ECS has native integration, so it
    will not invoke this.
    :return:
    """
    namespace_id = get_namespace_id(namespace_name)
    print('deregistering {} service and instance Id {} from namespace_id {}'.format(
        service_name, instance_ip, namespace_id))

    service_id = get_service_id(namespace_id, service_name)
    if service_id is None:
        print('INFO: Service: {} does not exist, no need to de-register instance'.format(service_name))
        exit(0)

    response = CLIENT.deregister_instance(ServiceId=service_id, InstanceId=instance_ip)
    status = get_operation_status(response['OperationId'])
    while status not in ('SUCCESS', 'FAILED', 'FAIL'):
        print('Sleeping for 10 seconds')
        time.sleep(10)
        status = get_operation_status(response['OperationId'])
        print("Operation status is: {}".format(status))
    print("Deregistration completed with status: {}".format(status))

def read_metadata_file(file):
    with open(file, 'r') as file_handle:
        metadata = json.load(file_handle)
        return metadata['NamespaceName'], metadata['ServiceName'], metadata['Port']
    raise("Error reading metadata file: {}".format(file))

if __name__ == "__main__":
    # Get some values from EC2 metadata service
    EC2_METADATA_URL = 'http://169.254.169.254/latest/meta-data'
    IP_ADDRESS = requests.get(EC2_METADATA_URL + "/public-ipv4").text
    MACS = requests.get(EC2_METADATA_URL + '/network/interfaces/macs/').text.split("\n")
    VPC_ID = requests.get(EC2_METADATA_URL + '/network/interfaces/macs/' + MACS[0] + 'vpc-id').text

    PARSER = argparse.ArgumentParser(
        description='register/de-register this instance from route53 servicediscovery')
    PARSER.add_argument('--action', required=True, dest='action',
                        choices=['register-instance', 'deregister-instance'],
                        help="specifies the action to be performed")
    PARSER.add_argument('--metadata', required=True, dest='metadata',
                        help="specifies the metadata json file")
    ARGS = PARSER.parse_args()
    namespace, service, port = read_metadata_file(ARGS.metadata)

    if ARGS.action == 'register-instance':
        # register(namespace_name, service_name, protocol, instance_ip, port, api_gateway_url, VPC_ID)
        register(namespace, service, 'DNS', IP_ADDRESS, port, None, VPC_ID)
    elif ARGS.action == 'deregister-instance':
        # deregister(namespace_name, service_name, instance_ip)
        deregister(namespace, service, IP_ADDRESS)
    else:
        print("ERROR: Invalid action")
        exit(127)
