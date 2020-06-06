import Adafruit_DHT
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class DHT22(object):

    def __init__(self):
        self.pin = os.getenv('pin_number_dht')
        self.dht_sensor = Adafruit_DHT.DHT22

    def take_reading(self):
        # return self.dht_sensor.humidity, self.dht_sensor.temperature
        return Adafruit_DHT.read_retry(self.dht_sensor, self.pin)
