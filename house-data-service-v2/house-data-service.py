from flask import Flask, g, jsonify, abort
import boto3

app = Flask(__name__)

client = boto3.client('dynamodb')

@app.route("/last_temps/<int:node>")
def last_temps(node):
    response = client.query(
        TableName='HouseData',
        KeyConditionExpression='Node = :node',
        ExpressionAttributeValues={
            ':node': {
                'N': str(node)
            }
        },
        ScanIndexForward=False,
        Limit=1
    )

    if response['Count'] == 0:
        return jsonify(message="no data for node"), 404

    item = response['Items'][0]
    print(item)
    dt = item['ItemDateTime']['S']
    try:
        temp = float(item['Values']['M']['Temperature']['N'])
    except KeyError:
        temp = 0
    try:    
        rssi = int(item['RSSI']['N'])
    except KeyError:
        rssi = 0

    return jsonify({'temp': temp, 'time': dt, 'rssi': rssi})
