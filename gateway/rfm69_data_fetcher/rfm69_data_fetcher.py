import time
import sys
from datetime import datetime
import paho.mqtt.client as mqtt

# RFM69 Python module for Raspberry Pi https://github.com/etrombly/RFM69
import RFM69.RFM69 as RFM69
from RFM69.RFM69registers import *

rfm69 = RFM69.RFM69(RF69_433MHZ, 1, 100, False, intPin=22, rstPin=18)
rfm69.encrypt("sampleEncryptKey")

MQTT_SERVER = "192.168.0.147"
MEASUREMENT_TYPES = [("temperature", "sensors/temp/"), ("humidity", "sensors/humidity/")]


def get_rfm69_data():
    if rfm69.receiveDone():
        rfm69_sender = rfm69.SENDERID
        rfm69_data = rfm69.DATA
        rfm69_rssi = rfm69.RSSI
        rfm69.receiveBegin()

        measurements = {}

        node_type = chr(rfm69_data[0])
        if node_type == "R":
            # RHT03 node
            valInt = rfm69_data[1] << 8 | rfm69_data[2]
            measurements["humidity"] = valInt / 10
            # MSB is high when temperature is negative
            valInt = (rfm69_data[3] & 0x7f) << 8 | rfm69_data[4]
            if rfm69_data[3] & 0x80:
                valInt = -valInt
            measurements["temperature"] = valInt / 10

        else:
            # DS18B20 node
            temp_data_msb = rfm69_data[0]
            temp_data_lsb = rfm69_data[1]
            if len(rfm69_data) > 2:
                temp_data_msb = rfm69_data[1]
                temp_data_lsb = rfm69_data[2]

            valHex = "0x%02x%02x" % (temp_data_msb, temp_data_lsb)
            valInt = int(valHex, 16)
            tempWhole = valInt >> 4
            tempWhole = -(tempWhole & 0x800) | (tempWhole & 0x7ff)
            tempFrac = float(0)
            if valInt & 0x08:
                tempFrac += 0.5
            if valInt & 0x04:
                tempFrac += 0.25
            if valInt & 0x02:
                tempFrac += 0.125
            if valInt & 0x01:
                tempFrac += 0.0625

            measurements["temperature"] = float(tempWhole) + tempFrac

        return rfm69_sender, measurements, rfm69_rssi


def publish_mqtt_message(topic, node, measurement, rssi):
    message = str(measurement) + ' ' + str(rssi)
    print(str(datetime.now()))
    print(node)
    print(topic)
    print(message)

    try:
        client = mqtt.Client()
        client.connect(MQTT_SERVER)
        client.publish(topic + node, message)
    except OSError as err:
        print("OS error: {0}".format(err))


while True:
    try:
        rfm69_data = get_rfm69_data()
        if rfm69_data:
            node = str(rfm69_data[0])
            measurements = rfm69_data[1]
            rssi = rfm69_data[2]

            for measurement_type in MEASUREMENT_TYPES:
                if measurement_type[0] in measurements:
                    publish_mqtt_message(
                        measurement_type[1],
                        node,
                        measurements[measurement_type[0]],
                        rssi
                    )

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("shutting down")
        rfm69.shutdown()
        sys.exit()
