"""
    register a micro service
"""
import datetime
import time
import boto3

CLIENT = boto3.client('servicediscovery')
CLIENT._endpoint.host = 'https://servicediscovery.us-west-2.amazonaws.com'  # pylint: disable=W0212
CLIENT._endpoint.verify = False  # pylint: disable=W0212


def list_namespaces(namespace_name):
    """
    list namespaces
    :param namespace_name:
    :return:
    """
    namespace_id = None
    list_ns_resp = CLIENT.list_namespaces()
    try:
        for ns_key in list_ns_resp.get('Namespaces'):
            if ns_key.get('Name') == namespace_name:
                print('Namespace already exists')
                namespace_id = ns_key.get('Id')
                break
            if namespace_id is not None:
                print('Breaking for loop')
                break
    except:
        print('Exception occurred')
    finally:
        print('Moving on from list_namespaces')
    return namespace_id


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
    print(
        'Namespace ID else loop {}, operation response {} and operation Id {}'.
        format(namespace_id, get_op_id_resp, op_id))
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
    service_id = None
    try:
        create_srv_resp = CLIENT.create_service(
            Name=service_name,
            DnsConfig={
                'NamespaceId': namespace_id,
                'RoutingPolicy': 'MULTIVALUE',
                'DnsRecords': [
                    {
                        'Type': 'A',
                        'TTL': 100
                    },
                ]
            },
            Description='Created by HTTP service registry')
        print('create service response {}'.format(create_srv_resp))
        service_id = create_srv_resp.get('Service').get('Id')
        print('service_id {}'.format(create_srv_resp.get('Service').get('Id')))
    except CLIENT.exceptions.ServiceAlreadyExists:
        print('ServiceAlreadyExists')
        list_srv_resp = CLIENT.list_services()
        for srv_key in list_srv_resp.get('Services'):
            if srv_key.get('Name') == service_name:
                service_id = srv_key.get('Id')
                print('found pre-existing serviceId {}'.format(service_id))
    return service_id


def create_http_service(namespace_id, service_name):
    """
    Create HTTP Service
    :param namespace_id:
    :param service_name:
    :return:
    """
    service_id = None
    # Create service
    try:
        create_srv_resp = CLIENT.create_service(
            Name=service_name, NamespaceId=namespace_id)
        print('create_srv_resp HTTP {}'.format(create_srv_resp))
        service_id = create_srv_resp.get('Service').get('Id')
        print('Create HTTP Service response {}'.format(create_srv_resp))
        print('HTTP Service ID {}'.format(
            create_srv_resp.get('Service').get('Id')))
    except CLIENT.exceptions.ServiceAlreadyExists:
        print('ServiceAlreadyExists')
        list_srv_resp = CLIENT.list_services()
        for srv_key in list_srv_resp.get('Services'):
            print('service key {}'.format(srv_key))
            if srv_key.get('Name') == service_name:
                service_id = srv_key.get('Id')
                print('Obtained the pre-existing serviceId {}'.format(
                    service_id))
    return service_id


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
    except:
        print('Error while registering the instance')
    finally:
        print('Moving on from register instance call')


def register_dns_instance(service_id, instance_id, port):
    """
    Register DNS Instance
    :param service_id:
    :param instance_id:
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
    reg_inst_resp = CLIENT.register_instance(
        ServiceId=service_id,
        InstanceId=instance_id,
        CreatorRequestId=creator_request_id,
        Attributes={
            'AWS_INSTANCE_IPV4': instance_id,
            'AWS_INSTANCE_PORT': port
        })
    print('Response from register_dns_instance {}'.format(reg_inst_resp))


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
             protocol, instance_id, port,
             api_gateway_url, vpc_id):
    """
    perform registration action with Route 53 for DNS based microservice.
    These are the EC2 and ECS microservices. ECS has native integration, so it
    will not invoke this.
    :return:
    """
    print('registering {} service and instance Id {}'.format(
        service_name, instance_id))

    # Check if the namespace exists, if not create it
    # Get/Create HTTP namespace ID
    namespace_id = list_namespaces(namespace_name)
    if namespace_id is None and protocol == 'HTTP':
        namespace_id, namespace_status, op_id = create_http_namespace(
            namespace_name)
        print(
            'create_http_namespace returned namespace_id {} status {}'.format(
                namespace_id, namespace_status))
        # TODO: Could be improved in future.
        # Just sleep and check after 2 minutes.
        while namespace_status not in ('SUCCESS', 'FAILED'):
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
        while namespace_status not in ('SUCCESS', 'FAILED'):
            print('Sleeping 2 minutes')
            time.sleep(120)
            namespace_status = get_operation_status(op_id)
    if protocol == 'HTTP' and namespace_id is not None:
        # No need to create service
        service_id = create_http_service(namespace_id, service_name)
        register_http_instance(api_gateway_url, service_id)
    elif protocol == 'DNS' and namespace_id is not None:
        # Create the service
        service_id = create_service(namespace_id, service_name)
        # Register instance
        register_dns_instance(service_id, instance_id, port)


# Tested cases: #1: pre-existing namespace, service create, register instance


def lambda_handler(event, context):
    """
    lambda handler function
    :param event:
    :param context:
    :return:
    """
    print('Lambda event {}'.format(event))

    del context
    namespace_name = event.get('NamespaceName', None)
    service_name = event.get('ServiceName', None)
    protocol = event.get('Protocol', None)
    instance_id = event.get('instanceId', None)
    port = event.get('port', None)
    api_gateway_url = event.get('apiGatewayUrl', None)
    vpc_id = event.get('vpcId', None)

    register(namespace_name, service_name, protocol, instance_id, port,
             api_gateway_url, vpc_id)


# Local test in dev environment
if __name__ == '__main__':
    TEST_EVENT = {
        'NamespaceName': 'frosting',
        'ServiceName': 'frosting',
        'Protocol': 'HTTP',  # or DNS
        # 'instanceId': '1.2.3.4',
        'port': '80',
        'apiGatewayUrl':
        'https://acwpv3segi.execute-api.us-west-2.amazonaws.com'
        # 'vpcId': 'vpc-00000000000000000'
    }
    lambda_handler(TEST_EVENT, '')
