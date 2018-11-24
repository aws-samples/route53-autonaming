"""
    deregister a micro service
"""
import boto3


def deregister(service_name, instance_id):
    """
    perform deregistration action with Route 53
    :return:
    """
    print('deregistering ' + service_name)
    client = boto3.client('servicediscovery')
    client.deregister_instance(ServiceId=service_name, InstanceId=instance_id)


def handler(event, context):
    """
    lambda handler function
    :param event:
    :param context:
    :return:
    """
    del context
    service_id = event.get('ServiceName') if event.get('ServiceName') else None
    instance_id = event.get('InstanceId') if event.get('InstanceId') else None
    deregister(service_id, instance_id)


if __name__ == '__main__':
    TEST_EVENT = {
        'ServiceId': 'srv-a1a1a1a1a1a1a1a1',
        'InstanceId': '11111111-aaaa-2222-bbbb-333333333333'
    }
    handler(TEST_EVENT, '')
