from flask import Flask, g, jsonify, abort
import boto3

app = Flask(__name__)

client = boto3.client('dynamodb')

@app.route("/last_temps/<int:node>")
def last_temps(node):
    node_and_type = '{}_T'.format(str(node))
    response = client.query(
        TableName='HouseData',
        KeyConditionExpression='NodeAndType = :node_and_type',
        ExpressionAttributeValues={
            ':node_and_type': {
                'S': str(node_and_type)
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
        temp = float(item['Value']['N'])
    except KeyError:
        temp = 0
    try:    
        rssi = int(item['RSSI']['N'])
    except KeyError:
        rssi = 0

    return jsonify({'temp': temp, 'time': dt, 'rssi': rssi})
