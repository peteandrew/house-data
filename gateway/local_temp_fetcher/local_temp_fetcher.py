import time
import sys
import paho.mqtt.client as mqtt

import gpio_temp

# Time interval of local temp sensor readings in seconds
GPIO_TEMP_TIME_INTERVAL = 60

client = mqtt.Client()
client.connect('localhost')

while True:
    try:
        curr_gpio_temp = gpio_temp.read_temp()
        if curr_gpio_temp == None:
            print "Error reading GPIO temp"
        else:
            client.publish('temps', '1 ' + str(curr_gpio_temp) + ' 0')

        time.sleep(GPIO_TEMP_TIME_INTERVAL)

    except KeyboardInterrupt:
        print "shutting down"
        sys.exit()
