import time
import sqlite3
import sys

# RFM69 Python module for Raspberry Pi https://github.com/etrombly/RFM69
import RFM69.RFM69 as RFM69
from RFM69.RFM69registers import *

import gpio_temp

# Time interval of local temp sensor readings in seconds
GPIO_TEMP_TIME_INTERVAL = 60


db_conn = sqlite3.connect('temps.db')
c = db_conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS temps (node integer, time text, rssi integer, temp real)")
db_conn.commit()

rfm69 = RFM69.RFM69(RF69_433MHZ, 1, 100, False, intPin=22, rstPin=18)
rfm69.encrypt("sampleEncryptKey")


last_gpio_temp_time = 0
def get_gpio_temp():
    global last_gpio_temp_time

    if time.time() - last_gpio_temp_time >= GPIO_TEMP_TIME_INTERVAL:
        last_gpio_temp_time = time.time()
        curr_gpio_temp = gpio_temp.read_temp()
        if curr_gpio_temp == None:
            print "Error reading GPIO temp"
        return curr_gpio_temp


def get_rfm69_temp():
    if rfm69.receiveDone():
        rfm69_sender = rfm69.SENDERID
        rfm69_data = rfm69.DATA
        rfm69_rssi = rfm69.RSSI
        rfm69.receiveBegin()

        valHex = "0x%x%x" % (rfm69_data[0], rfm69_data[1])
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
        curr_gpio_temp = get_gpio_temp()
        if curr_gpio_temp:
            print curr_gpio_temp
            c = db_conn.cursor()
            c.execute("INSERT INTO temps VALUES (1, datetime('now'), 0, ?)", (curr_gpio_temp,))
            db_conn.commit()

        rfm69_temp = get_rfm69_temp()
        if rfm69_temp:
            print rfm69_temp
            c = db_conn.cursor()
            c.execute("INSERT INTO temps VALUES (?, datetime('now'), ?, ?)", (rfm69_temp[0], rfm69_temp[2], rfm69_temp[1]))
            db_conn.commit()

        time.sleep(0.01)

    except KeyboardInterrupt:
        print "shutting down"
        rfm69.shutdown()
        db_conn.commit()
        db_conn.close()
        sys.exit()
