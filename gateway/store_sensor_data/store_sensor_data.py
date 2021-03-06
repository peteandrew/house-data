import time
import sqlite3
import os
import sys
import paho.mqtt.client as mqtt

def on_temp_message(client, userdata, msg):
    node = msg.topic.split('/')[2]
    msg_components = str(msg.payload)[2:-1].split(' ')
    print('Temperature reading')
    print(node)
    print(msg_components)
    try:
        c = db_conn.cursor()
        c.execute("INSERT INTO temps VALUES (?, datetime('now'), ?, ?)", (int(node), int(msg_components[1]), float(msg_components[0])))
        db_conn.commit()
    except sqlite3.OperationalError as e:
        print(e)

def on_humidity_message(client, userdata, msg):
    node = msg.topic.split('/')[2]
    msg_components = str(msg.payload)[2:-1].split(' ')
    print('Humidity reading')
    print(node)
    print(msg_components)
    try:
        c = db_conn.cursor()
        c.execute("INSERT INTO humidities VALUES (?, datetime('now'), ?, ?)", (int(node), int(msg_components[1]), float(msg_components[0])))
        db_conn.commit()
    except sqlite3.OperationalError as e:
        print(e)

def on_pressure_message(client, userdata, msg):
    node = msg.topic.split('/')[2]
    msg_components = str(msg.payload)[2:-1].split(' ')
    print('Pressure reading')
    print(node)
    print(msg_components)
    try:
        c = db_conn.cursor()
        c.execute("INSERT INTO pressures VALUES (?, datetime('now'), ?, ?)", (int(node), int(msg_components[1]), float(msg_components[0])))
        db_conn.commit()
    except sqlite3.OperationalError as e:
        print(e)


db_file = os.environ.get('SENSOR_DB_FILE', 'sensor_data.db')
db_conn = sqlite3.connect(db_file)

c = db_conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS temps (node integer, time text, rssi integer, temp real)")
c.execute("CREATE TABLE IF NOT EXISTS humidities (node integer, time text, rssi integer, humidity real)")
c.execute("CREATE TABLE IF NOT EXISTS pressures (node integer, time text, rssi integer, pressure real)")
db_conn.commit()

client = mqtt.Client()

client.message_callback_add('sensors/temp/+', on_temp_message)
client.message_callback_add('sensors/humidity/+', on_humidity_message)
client.message_callback_add('sensors/pressure/+', on_pressure_message)

client.connect('localhost')

client.subscribe('sensors/temp/+')
client.subscribe('sensors/humidity/+')
client.subscribe('sensors/pressure/+')

client.loop_forever()
