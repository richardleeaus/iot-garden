import math
import sys
import time
import os
from grove.adc import ADC
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class GroveLightSensor:

    def __init__(self):
        self.channel = int(os.environ.get("analogue_channel_light"))
        self.adc = ADC()

    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value


def main():
    sensor = GroveLightSensor()

    print('Detecting light...')
    while True:
        print('Light value: {0}'.format(sensor.light))
        time.sleep(1)

if __name__ == '__main__':
    main()