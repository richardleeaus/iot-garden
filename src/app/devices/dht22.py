import Adafruit_DHT
import board


class DHT22(object):

    def __init__(self, pin):
        self.pin = pin
        self.dht_sensor = Adafruit_DHT.DHT22

    def take_reading(self):
        # return self.dht_sensor.humidity, self.dht_sensor.temperature
        return Adafruit_DHT.read_retry(self.dht_sensor, self.pin)
