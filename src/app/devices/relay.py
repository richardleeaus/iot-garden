import time
import os
from grove.grove_relay import GroveRelay
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class Relay(object):
    def __init__(self):
        self.pin = os.getenv('pin_number_pump')
        self.relay = GroveRelay(self.pin)

    def trigger(self):

        try:
            print("Water pump on")
            self.relay.on()
            time.sleep(3)
            self.relay.off()
            print("Water pump off")
            time.sleep(5)
        finally:
            self.relay.off()

    def trigger(self, seconds):
        try:
            print("Water pump on")
            self.relay.on()
            time.sleep(seconds)
            self.relay.off()
            print("Water pump off")
            time.sleep(5)
        finally:
            self.relay.off()

if __name__=="__main__":
   relay = Relay()
   relay.trigger(2)