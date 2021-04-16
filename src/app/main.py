import RPi.GPIO as GPIO
import time
import logging
import os
import asyncio
import threading
import functools
import uuid
import json

from tabulate import tabulate
from opencensus.ext.azure.log_exporter import AzureLogHandler
from dotenv import load_dotenv, find_dotenv
# from devices.mcp3008 import MoistureSensor
from devices.moisture_sensor import MoistureSensor
from devices.dht22 import DHT22
from devices.relay import Relay
from db.water_db import WaterDatabase
from datetime import datetime
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse, Message

PUMP_SECONDS = os.getenv('pump_seconds', 5)
WATERING_DELAY_MINUTES = os.getenv('watering_delay_minutes', 5)
MOISTURE_WATERING_LIMIT = os.getenv('moisture_watering_limit', 30)

load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey={}'.format(
            os.getenv('log_analytics_instrumentation_key'))))
logger.setLevel(level=os.environ.get('log_level'))


async def pump_water_command(device_client, method_request):
    # method_request = await device_client.receive_method_request(
    #     "pump_water"
    # )  # Wait for method1 calls

    water_plant()

    payload = {"result": True}  # set response payload
    status = 200  # set return status code

    method_response = MethodResponse.create_from_method_request(
        method_request, status, payload
    )
    await device_client.send_method_response(method_response)


async def get_plant_metrics_command(device_client, method_request):
    # method_request = await device_client.receive_method_request(
    #     "get_plant_metrics"
    # )  # Wait for method1 calls

    readings = get_readings()
    payload = {"result": True, "data": readings}  # set response payload
    status = 200  # set return status code
    print("Sending plant metrics to IoT Hub")

    method_response = MethodResponse.create_from_method_request(
        method_request, status, payload
    )
    await device_client.send_method_response(method_response)


commands = {
    'pump_water': pump_water_command,
    'get_plant_metrics': get_plant_metrics_command,
}


async def command_listener(device_client):
    while True:
        method_request = await device_client.receive_method_request()  # Wait for commands
        print("Command received...")
        await commands[method_request.name](device_client, method_request)


def water_plant():
    print('Watering plant!')
    pump.trigger(PUMP_SECONDS)

    # create local cache
    localdb.create_water_log(0, PUMP_SECONDS)


def get_readings():
    # Read the moisture sensor data
    moisture_level = moisture_sensor.get_moisture()
    moisture_percent_scaled = moisture_sensor.GetScaledPercent()
    # humidity, temperature = dht22.take_reading()
    temperature,pressure,humidity = bme280.readBME280All()

    readings = {
        'custom_dimensions': {
            'soil_moisture_percent': moisture_percent_scaled,
            'humidity': humidity,
            'temperature': temperature,
            'pressure': pressure
        }
    }
    logger.info('Plant log', extra=readings)
    return readings


def init():
    global moisture_sensor
    global pump
    global dht22
    global localdb
    global device_client

    conn_str = os.getenv("iot_connection_string")
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    moisture_sensor = MoistureSensor()
    pump = Relay()
    # Using Grove PI instead
    # dht22 = DHT22()
    bme280 = BME280()
    localdb = WaterDatabase()


async def send_test_message(i):
    i["timestamp"] = str(datetime.utcnow())
    msg = Message(json.dumps(i))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    msg.message_id = uuid.uuid4()
    await device_client.send_message(msg)
    print("done sending message #" + str(i))


async def worker():

    while True:

        # Get readings
        readings = get_readings()

        # Print out values
        print(
            tabulate(
                tabular_data=list(readings['custom_dimensions'].items()),
                headers=['Measure', 'Value'],
                tablefmt="simple"))
        print("")

        # Send data to IoT Hub
        await asyncio.gather(send_test_message(dict(readings['custom_dimensions'].items())))

        # Only water if there is less than % <moisture>, and have you haven't
        # watered in the last <duration>
        if readings['custom_dimensions']['soil_moisture_percent'] <= MOISTURE_WATERING_LIMIT and \
                localdb.get_pump_seconds_duration_in_last(
                    WATERING_DELAY_MINUTES) == 0:
            water_plant(readings)
            await asyncio.gather(send_test_message({
                "water_duration_seconds": PUMP_SECONDS
            }))

        # Wait before repeating loop
        logger.info('Waiting for {} seconds'.format(moisture_sensor.delay))
        time.sleep(moisture_sensor.delay)


async def main():

    init()

    await device_client.connect()

    listeners = asyncio.gather(
        command_listener(device_client),
        worker(),
    )

    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished

    # cancel tasks
    listeners.add_done_callback(lambda r: r.exception())
    listeners.cancel()
    await device_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
