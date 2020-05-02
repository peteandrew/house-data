import smbus
import bme280
import time
import paho.mqtt.client as mqtt

MQTT_HOST = '192.168.0.147'

port = 1
address = 0x77
bus = smbus.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

def publish_temperature(data):
    client = mqtt.Client()
    client.connect(MQTT_HOST)
    message = '1 ' + str(data.temperature) + ' 0'
    client.publish('temp', message)

def publish_humidity(data):
    client = mqtt.Client()
    client.connect(MQTT_HOST)
    message = '1 ' + str(data.humidity) + ' 0'
    client.publish('humidity', message)

def publish_pressure(data):
    client = mqtt.Client()
    client.connect(MQTT_HOST)
    message = '1 ' + str(data.pressure) + ' 0'
    client.publish('pressure', message)

min_count = 0

while True:
    data = bme280.sample(bus, address, calibration_params)
    print(data)

    if min_count % 2 == 0:
        publish_temperature(data)
        publish_humidity(data)
    if min_count % 10 == 0:
        publish_pressure(data)

    time.sleep(60)
    min_count += 1
