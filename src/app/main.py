import RPi.GPIO as GPIO
import time
import logging
import os
import psycopg2

from tabulate import tabulate
from opencensus.ext.azure.log_exporter import AzureLogHandler
from dotenv import load_dotenv, find_dotenv
from devices.mcp3008 import MoistureSensor
from devices.dht22 import DHT22
from devices.relay import Relay
from db.water_db import WaterDatabase
from psycopg2.extras import execute_values
from db.historian import TimescaleDB
from datetime import datetime

PUMP_SECONDS = 5
WATERING_DELAY_MINUTES = 5

load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey={}'.format(
            os.getenv('log_analytics_instrumentation_key'))))
logger.setLevel(level=logging.INFO)

# Using a dikt as we have multiple analogue sensors, and we may choose
# one over the other
analogue_devices = {
    "mcp3008": MoistureSensor(18, 23, 24, 25, 4)
}


def water_plant(readings, localdb, pump):
    print('Watering plant!')
    pump.trigger(PUMP_SECONDS)

    # create local cache
    localdb.create_water_log(0, PUMP_SECONDS)

def main(localdb, historiandb, moisture_sensor, pump, dht22):

    while True:

        # Read the moisture sensor data
        moisture_level = moisture_sensor.ReadChannel()
        moisture_percent_scaled = moisture_sensor.GetScaledPercent()
        humidity, temperature = dht22.take_reading()

        readings = {
            'custom_dimensions': {
                'soil_moisture_percent':
                    "{}".format(moisture_percent_scaled),
                'humidity': humidity,
                'temperature': temperature
            }
        }
        logger.info('Plant log', extra=readings)

        # Print out values
        print(
            tabulate(
                tabular_data=list(readings['custom_dimensions'].items()), 
                headers=['Measure', 'Value'], 
                tablefmt="simple"))
        print("")

        # Log into remote DB
        records = []
        for key, value in readings['custom_dimensions'].items():
            records.append((datetime.utcnow(), key, value))
        historiandb.insert_sensor_records(records)

        # Only water if there is less than % <moisture>, and have you haven't
        # watered in the last <duration>
        if moisture_percent_scaled <= 60 and \
                localdb.get_pump_seconds_duration_in_last(WATERING_DELAY_MINUTES) == 0:
            water_plant(readings, localdb, pump)

        # Wait before repeating loop
        logger.info('Waiting for {} seconds'.format(moisture_sensor.delay))
        time.sleep(moisture_sensor.delay)


if __name__ == "__main__":
    main(
        localdb=WaterDatabase(), 
        historiandb=TimescaleDB(),
        moisture_sensor=analogue_devices.get(os.getenv('analogue_device'), 'mcp3008'),
        pump=Relay(os.getenv('pin_number_pump')),
        dht22=DHT22(os.getenv('pin_number_dht'))
    )
