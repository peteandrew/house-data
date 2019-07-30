import boto3
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
    response = client.put_item(
        TableName='HouseData',
        Item={
            'Node': {
                'N': str(row[0]),
            },
            'DateTime': {
                'S': row[1]
            },
            'RSSI': {
                'N': str(row[3])
            },
            'Values': {
                'M': {
                    'Temp': {
                        'N': str(row[2])
                    }
                }
            }
        }
    )
    print(response)
cur.close()
