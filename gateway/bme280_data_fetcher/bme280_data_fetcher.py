import smbus2
import bme280
import time
import paho.mqtt.client as mqtt

port = 0
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

while True:
    data = bme280.sample(bus, address, calibration_params)
    print(data)

    client = mqtt.Client()
    client.connect('localhost')

    message = '1 ' + str(data.temperature) + ' 0'
    client.publish('temp', message)

    message = '1 ' + str(data.pressure) + ' 0'
    client.publish('pressure', message)

    message = '1 ' + str(data.humidity) + ' 0'
    client.publish('humidity', message)

    time.sleep(60)
