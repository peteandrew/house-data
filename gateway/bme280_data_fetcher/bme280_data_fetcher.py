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
    try:
        client = mqtt.Client()
        client.connect(MQTT_HOST)
        message = str(data.temperature) + ' 0'
        client.publish('sensors/temp/1', message)
    except OSError as err:
        print("OS error: {0}".format(err))

def publish_humidity(data):
    try:
        client = mqtt.Client()
        client.connect(MQTT_HOST)
        message = str(data.humidity) + ' 0'
        client.publish('sensors/humidity/1', message)
    except OSError as err:
        print("OS error: {0}".format(err))

def publish_pressure(data):
    try:
        client = mqtt.Client()
        client.connect(MQTT_HOST)
        message = str(data.pressure) + ' 0'
        client.publish('sensors/pressure/1', message)
    except OSError as err:
        print("OS error: {0}".format(err))

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
