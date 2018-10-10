import time
import sqlite3
import sys
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    msg_components = str(msg.payload).split(' ')
    print msg_components
    c = db_conn.cursor()
    c.execute("INSERT INTO temps VALUES (?, datetime('now'), ?, ?)", (int(msg_components[0]), int(msg_components[2]), float(msg_components[1])))
    db_conn.commit()


db_conn = sqlite3.connect('temps.db')
c = db_conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS temps (node integer, time text, rssi integer, temp real)")
db_conn.commit()

client = mqtt.Client()
client.on_message = on_message
client.connect('localhost')

client.subscribe('temps')

client.loop_forever()
