import Adafruit_DHT


class DHT22(object):

    def __init__(self, pin):
        self.pin = pin
        self.dht_sensor = Adafruit_DHT.DHT22

    def take_reading(self):
        return Adafruit_DHT.read_retry(self.dht_sensor, self.pin)
