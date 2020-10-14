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
    # Table Name from environment variables
    table_name = os.environ['TABLE_NAME']
    
    table = dynamodb.Table(table_name)
    pokemon_name = event['pathParameters']['name']
    kargs = {
        'IndexName': 'InvertedIndex',
        'KeyConditionExpression': Key('SK').eq(f'Pokemon#{pokemon_name}')
    }
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
