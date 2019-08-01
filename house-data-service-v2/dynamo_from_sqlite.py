import boto3
import botocore
import sqlite3
import sys

if len(sys.argv) < 2:
    print('Must supply source db filename')
    sys.exit(1)

db_filename = sys.argv[1]
db = sqlite3.connect(db_filename)

client = boto3.client('dynamodb')

cur = db.execute('SELECT node, time, temp, rssi FROM temps ORDER BY time')
for row in cur:
    print(row)
    try:
        response = client.put_item(
            TableName='HouseData',
            ConditionExpression='attribute_not_exists(Node) AND attribute_not_exists(ItemDateTime)',
            Item={
                'Node': {
                    'N': str(row[0]),
                },
                'ItemDateTime': {
                    'S': row[1]
                },
                'RSSI': {
                    'N': str(row[3])
                },
                'Values': {
                    'M': {
                        'Temperature': {
                            'N': str(row[2])
                        }
                    }
                }
            }
        )
        print(response)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("Item already exists")
cur.close()
