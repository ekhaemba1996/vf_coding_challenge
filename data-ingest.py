import json
import boto3
import csv
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def get_pokemon_meta(row):
    row['PK'] = f"PrimaryType#{row.pop('Type 1')}"
    row['SK'] = f"Pokemon#{row.pop('Name')}"
    row['Data'] = f"SecondaryType#{row.pop('Type 2')}"
    row['PokedexId'] = row.pop('#')
    row['Total'] = int(row['Total'])
    return row
    
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
    records = []
    with table.batch_writer() as batch:
        for row in csv_data:
            records.append(get_pokemon_meta(row))
        for rec in records:
            batch.put_item(Item=rec)
    body = {
        "message": f"Data Ingestion function executed successfully! Created pokemon {len(records)}records",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
