import json
import boto3
import csv
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def readRow(row, batch):
    # Update keys
    row['PokedexId'] = row.pop('#')
    row['Type'] = row.pop('Type 1')
    row['SecondaryType'] = row.pop('Type 2')
    row['StatSum'] = int(row.pop('Total'))
    response = batch.put_item(Item=row)
    print("Added pokemon", row['Name'])

def handle(event, context):
    # Key and Bucket Name from environment variables
    bucket_name = os.environ['BUCKET_NAME']
    key = os.environ['DATA_KEY']
    table_name = os.environ['TABLE_NAME']
    # Get file from s3 and parse into csv dictionary object
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    csvcontent = obj['Body'].read().decode('utf-8').splitlines(True)
    csv_data = csv.DictReader(csvcontent)

    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for row in csv_data:
            readRow(row, batch)
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
