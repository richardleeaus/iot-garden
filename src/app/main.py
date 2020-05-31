import RPi.GPIO as GPIO
import time
import logging
import os

from opencensus.ext.azure.log_exporter import AzureLogHandler
from dotenv import load_dotenv, find_dotenv
from devices.mcp3008 import MoistureSensor
from devices.dht22 import DHT22
from devices.relay import Relay
from db.water_db import WaterDatabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey={}'.format(
            os.getenv('log_analytics_instrumentation_key'))))
logger.setLevel(level=logging.INFO)

analogue_devices = {
    "mcp3008": MoistureSensor(18, 23, 24, 25, 4)
}

PUMP_SECONDS = 5
MOISTURE_SENSOR = analogue_devices.get(os.getenv('analogue_device'), 'mcp3008')
DHT22_SENSOR = DHT22(12)
pump = Relay(16)


def main():
    db = WaterDatabase()

    while True:

        # Read the moisture sensor data
        moisture_level = MOISTURE_SENSOR.ReadChannel()
        moisture_percent_scaled = MOISTURE_SENSOR.GetScaledPercent()
        humidity, temperature = DHT22_SENSOR.take_reading()

        # Print out results
        print("--------------------------------------------")
        print("Humidity:\t {0:0.1f}%".format(humidity))
        print("Tempearture:\t {0:0.1f}*C".format(temperature))
        print("Moisture:\t {}%".format(moisture_percent_scaled))
        print("Raw:\t\t {}".format(moisture_level))
        print("Max value:\t {:0.1f}".format(
                MOISTURE_SENSOR.GetScaledMaxValue()))

        readings = {
            'custom_dimensions': {
                'soil_moisture_percent':
                    "{}".format(moisture_percent_scaled),
                'soil_analogue_raw_value':
                    "{}".format(moisture_level),
                'soil_convert_max_value':
                    MOISTURE_SENSOR.GetScaledMaxValue(),
                'soil_sensor_in_water_reading':
                    MOISTURE_SENSOR.GetMinHunidityReading(),
                'soil_sensor_air_reading':
                    MOISTURE_SENSOR.GetMaxHumidityReading(),
                'humidity': humidity,
                'temperature': temperature
            }
        }
        logger.info('Plant log', extra=readings)

        if moisture_percent_scaled <= 60 and db.get_pump_seconds_duration(5) == 0:
            print('Trigger!')
            pump.trigger(PUMP_SECONDS)
            db.create_water_log(0, PUMP_SECONDS)

        # Wait before repeating loop
        time.sleep(MOISTURE_SENSOR.delay)


if __name__ == "__main__":
    main()
