import boto3
from datetime import datetime

client = boto3.client('dynamodb')

response = client.scan(
    TableName='HouseData'
)

print(response['Items'])
