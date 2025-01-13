# coding=utf-8

import time
import random

class Adafruit_DHT():

    DHT11 = 4
 
    def read_retry(t, p):
        time.sleep(random.randint(10,20) / 10)
        return random.randint(100, 200) / 10, random.randint(150, 300) / 10
