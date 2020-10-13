import json
import boto3
from boto3.dynamodb.conditions import Key
import csv
import os
import decimal

# https://stackoverflow.com/questions/16957275/python-to-json-serialization-fails-on-decimal
# For Serializing Decimal Objects returned from DDB
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
# Dynamo client
dynamodb = boto3.resource('dynamodb')

def handle(event, context):
    # Key and Bucket Name from environment variables
    table_name = os.environ['TABLE_NAME']
    
    table = dynamodb.Table(table_name)
    pokemon_type = event['pathParameters']['type']
    kargs = {
        'IndexName': 'StatIndex',
        'KeyConditionExpression': Key('Type').eq(pokemon_type)
    }

    if event['queryStringParameters'] and event['queryStringParameters']['min_sum']:
        try:
            min_sum = int(event['queryStringParameters']['min_sum'])
        except ValueError:
            print('Minimum Sum Exception')
            return {
                "statusCode": 400,
                "body": json.dumps({"errorReason":"Query Parameter 'min_sum' must be a valid integer"})
            }
        kargs['KeyConditionExpression'] = kargs['KeyConditionExpression'] & Key('StatSum').gt(min_sum)
    query_result = table.query(
        **kargs
    )
    body = {
        "result": query_result["Items"]
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body, default=decimal_default)
    }

    return response
