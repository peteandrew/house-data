import boto3
from datetime import datetime

client = boto3.client('dynamodb')

node = 1
dt = str(datetime.now())

response = client.put_item(
    TableName='HouseData',
    Item={
        'Node': {
            'N': str(node),
        },
        'DateTime': {
            'S': dt
        }
    }
)

print(response)
