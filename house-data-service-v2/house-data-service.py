from flask import Flask, g, jsonify, abort, request
import boto3
import botocore
import json


app = Flask(__name__)

client = boto3.client('dynamodb')


def get_node_data(request, node):
    types = []

    type = request.args.get('type')
    if type is not None:
        if type not in ['T', 'H', 'P']:
            return jsonify(message='type must be T, H or P'), 400
        types = [type]
    else:
        types = ['T', 'H', 'P']

    node_data = {}

    for type in types:
        node_and_type = '{}_{}'.format(str(node), type)
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
            continue

        item = response['Items'][0]
        dt = item['ItemDateTime']['S']
        try:
            value = float(item['Value']['N'])
        except KeyError:
            value = 0
        try:    
            rssi = int(item['RSSI']['N'])
        except KeyError:
            rssi = 0

        node_data[type] = {'value': value, 'time': dt, 'rssi': rssi}

    if len(node_data.keys()) == 0:
        return jsonify(message='no data found for node'), 404

    return jsonify(node_data)


def post_node_data(request, node):
    data = request.get_json()
    type = list(data.keys())[0]
    if type not in ['T', 'H', 'P']:
        return jsonify(message='type must be T, H or P'), 400

    sensor_data = data[type]
    required_attributes = ['time', 'value', 'rssi']
    for attribute in required_attributes:
        if attribute not in sensor_data.keys():
            return jsonify(message='required attribute {} not found'.format(attribute)), 400

    node_and_type = '{}_{}'.format(str(node), type)
    try:
        client.put_item(
            TableName='HouseData',
            ConditionExpression='attribute_not_exists(NodeAndType) AND attribute_not_exists(ItemDateTime)',
            Item={
                'NodeAndType': {
                    'S': node_and_type,
                },
                'ItemDateTime': {
                    'S': sensor_data['time']
                },
                'RSSI': {
                    'N': str(sensor_data['rssi'])
                },
                'Value': {
                    'N': str(sensor_data['value'])
                }
            }
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return jsonify(message="data already exists for sensor at that time"), 409

    return jsonify(message="created"), 201


@app.route("/nodes/<int:node>", methods=['GET', 'POST'])
def node_data(node):
    if request.method == 'GET':
        return get_node_data(request, node)
    else:
        return post_node_data(request, node)
