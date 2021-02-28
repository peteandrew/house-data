import time
import sys
from datetime import datetime
import paho.mqtt.client as mqtt

# RFM69 Python module for Raspberry Pi https://github.com/etrombly/RFM69
import RFM69.RFM69 as RFM69
from RFM69.RFM69registers import *

rfm69 = RFM69.RFM69(RF69_433MHZ, 1, 100, False, intPin=22, rstPin=18)
rfm69.encrypt("sampleEncryptKey")


def get_rfm69_temp():
    if rfm69.receiveDone():
        rfm69_sender = rfm69.SENDERID
        rfm69_data = rfm69.DATA
        rfm69_rssi = rfm69.RSSI
        rfm69.receiveBegin()

        node_type = chr(rfm69_data[0])
        if node_type == "R":
            valHex = "0x%02x%02x" % (rfm69_data[3], rfm69_data[4])
            valInt = int(valHex, 16)
            tempFull = valInt / 10

        else:
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

            tempFull = float(tempWhole) + tempFrac

        return rfm69_sender, tempFull, rfm69_rssi


while True:
    try:
        rfm69_temp = get_rfm69_temp()
        if rfm69_temp:
            node = str(rfm69_temp[0])
            message = str(rfm69_temp[1]) + ' ' + str(rfm69_temp[2])
            print(str(datetime.now()))
            print(node)
            print(message)

            try:
                client = mqtt.Client()
                client.connect('192.168.0.147')
                client.publish('sensors/temp/' + node, message)
            except OSError as err:
                print("OS error: {0}".format(err))

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("shutting down")
        rfm69.shutdown()
        sys.exit()
