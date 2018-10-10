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

        temp_data_msb = rfm69_data[0]
	temp_data_lsb = rfm69_data[1]
        if len(rfm69_data) > 2:
            print str(rfm69_data[0])
            temp_data_msb = rfm69_data[1]
	    temp_data_lsb = rfm69_data[2]

	print(temp_data_msb)
	print(temp_data_lsb)

        valHex = "0x%02x%02x" % (temp_data_msb, temp_data_lsb)
	print(valHex)
        valInt = int(valHex, 16)
        tempWhole = valInt >> 4
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
            print str(datetime.now())
            print 'in rfm69_data_fetcher.py'
            print rfm69_temp
            message = str(rfm69_temp[0]) + ' ' + str(rfm69_temp[1]) + ' ' + str(rfm69_temp[2])
            client = mqtt.Client()
            client.connect('localhost')
            client.publish('temps', message)

        time.sleep(0.1)

    except KeyboardInterrupt:
        print "shutting down"
        rfm69.shutdown()
        sys.exit()
