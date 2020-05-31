import RPi.GPIO as GPIO
import time
import logging
import os


from opencensus.ext.azure.log_exporter import AzureLogHandler
from dotenv import load_dotenv, find_dotenv
from devices.MoistureSensor import MoistureSensor
from devices.DHT22 import DHT22
from devices.Relay import Relay

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey={}'.format(
            os.getenv('log_analytics_instrumentation_key'))))
logger.setLevel(level=logging.INFO)

MOISTURE_SENSOR = MoistureSensor(18, 23, 24, 25, 4)
DHT22_SENSOR = DHT22(12)
RELAY = Relay(16)


def main():
    while True:

        # Read the moisture sensor data
        moisture_level = MOISTURE_SENSOR.ReadChannel()
        moisture_percent_scaled = MOISTURE_SENSOR.GetScaledPercent()
        humidity, temperature = DHT22_SENSOR.take_reading()

        RELAY.trigger()

        # Print out results
        print("--------------------------------------------")
        print("Humidity:\t {0:0.1f}%".format(humidity))
        print("Tempearture:\t {0:0.1f}*C".format(temperature))
        print("Moisture:\t {}%".format(moisture_percent_scaled))
        print("Raw:\t\t {}".format(moisture_level))
        print("Data:\t\t {}".format(moisture_level-MOISTURE_SENSOR.min_humidity_reading))
        print("Max value:\t {}".format(str(MOISTURE_SENSOR.max_humidity_reading - MOISTURE_SENSOR.min_humidity_reading)))

        properties = {
            'custom_dimensions':
                {
                    'soil_moisture_percent': "{}".format(moisture_percent_scaled),
                    'soil_analogue_raw_value': "{}".format(moisture_level),
                    'soil_convert_max_value': MOISTURE_SENSOR.max_humidity_reading - MOISTURE_SENSOR.min_humidity_reading,
                    'soil_sensor_in_water_reading': MOISTURE_SENSOR.min_humidity_reading,
                    'soil_srnsor_air_reading': MOISTURE_SENSOR.max_humidity_reading,
                    'humidity': humidity,
                    'temperature': temperature
                }
        }
        logger.info('Plant log', extra=properties)

        # Wait before repeating loop
        time.sleep(MOISTURE_SENSOR.delay)


if __name__ == "__main__":
    main()
