def lambda_handler(event, context):
    del event
    del context
    return_value = {'FrostingTypes': ['Vanilla', 'Chocolate', 'Strawberry', 'Cream Cheese']}
    return return_value
