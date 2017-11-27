#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
import sys
import sqlite3

conn = sqlite3.connect('temps.db')

test = RFM69.RFM69(RF69_433MHZ, 1, 100, False, intPin=22, rstPin=18)
test.encrypt("sampleEncryptKey")

while True:
    try:
        test.receiveBegin()
        while not test.receiveDone():
            time.sleep(.1)
	print test.DATA
    	valHex = "0x%x%x" % (test.DATA[0], test.DATA[1])
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

        print "%f RSSI:%s" % (tempFull, test.RSSI)

	c = conn.cursor()
	c.execute("INSERT INTO temps VALUES (datetime('now'), ?, ?)", (test.RSSI, tempFull))
	conn.commit()
    except KeyboardInterrupt:
        print "shutting down"
        test.shutdown()
        sys.exit()
