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
    pokemon_type = event['pathParameters']['type']
    kargs = {
        'IndexName': 'TotalIndex',
        'KeyConditionExpression': Key('PK').eq(f"PrimaryType#{pokemon_type}")
    }
    # Query string parameter parsing logic
    if event['queryStringParameters']:
        # Secondary is active if the 'secondary' query string passed is equal to 'true' 
        secondary = 'secondary' in event['queryStringParameters'] and event['queryStringParameters']['secondary'] == 'true'
        # Evaluate Secondary
        kargs['IndexName'] = 'SecondaryTypeIndex' if secondary else kargs['IndexName']
        kargs['KeyConditionExpression'] = Key('Data').eq(f"SecondaryType#{pokemon_type}") if secondary else kargs['KeyConditionExpression']

        # 'min_sum' is the minimum stat total to filter the query on 
        if 'min_sum' in event['queryStringParameters']:
            try:
                min_sum = int(event['queryStringParameters']['min_sum'])
            except ValueError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error":"Query parameter `min_sum` must be a valid integer"})
                }
            kargs['KeyConditionExpression'] = kargs['KeyConditionExpression'] & Key('Total').gt(min_sum)
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
