import boto3
from datetime import datetime

client = boto3.client('dynamodb')

response = client.query(
    TableName='HouseData',
    KeyConditionExpression='Node = :node',
    ExpressionAttributeValues={
        ':node': {
            'N': '3'
        }
    },
    ScanIndexForward=False,
    Limit=1
)

print(response['Items'])
