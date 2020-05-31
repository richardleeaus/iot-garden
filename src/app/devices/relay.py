import time
from gpiozero import LED
# motion_sensor = MotionSensor(4)


class Relay(object):
    def __init__(self, pin):
        self.pin = pin
        self.relay = LED(pin)

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
