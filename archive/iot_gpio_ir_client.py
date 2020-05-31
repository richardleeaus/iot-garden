import random
import time
import os
import sys
import iothub_client
import datetime
import time
from gpiozero import LED, MotionSensor, Buzzer
from iothub_client import (IoTHubClient, IoTHubClientError,
                           IoTHubTransportProvider)
from iothub_client import (IoTHubMessage, IoTHubMessageDispositionResult,
                           IoTHubError, DeviceMethodReturnValue)
from utils.powerbi import PowerBI
from dotenv import load_dotenv
load_dotenv()

# chose HTTP, AMQP or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.AMQP
CONNECTION_STRING = os.getenv('iot_connection_string')
MSG_TXT = \
    "{\"datetime\": \"%s\", " \
    "\"online\": %i, \"total\": %i}"
MESSAGE_COUNTER = 0
SEND_REPORTED_STATE_CALLBACKS = 0
SEND_CALLBACKS = 0
RECEIVE_CALLBACKS = 0

# GPIO - change these to match your GPIO
motion_sensor = MotionSensor(4)
led = LED(2)
buzzer = Buzzer(17)


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print("Confirmation[%d] received for message with result = %s" %
          (user_context, result))
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print("\tProperties: %s" % key_value_pair)
    SEND_CALLBACKS += 1
    print("\tTotal calls confirmed: %d" % SEND_CALLBACKS)


def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print("Confirmation for reported state received with:\n"
          "status_code = [%d]\ncontext = %s" % (status_code, user_context))

    SEND_REPORTED_STATE_CALLBACKS += 1
    print("Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS)


class HubManager(object):

    def __init__(
            self,
            connection_string,
            protocol=IoTHubTransportProvider.MQTT):
        self.client_protocol = protocol
        self.client = IoTHubClient(connection_string, protocol)
        if protocol == IoTHubTransportProvider.HTTP:
            self.client.set_option("timeout", TIMEOUT)
            self.client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)
        # set the time until a message times out
        self.client.set_option("messageTimeout", 100000)

    def send_event(self, event, properties, send_context):
        if not isinstance(event, IoTHubMessage):
            event = IoTHubMessage(bytearray(event, 'utf8'))
            event.set_content_encoding_system_property('utf-8')
            event.set_content_type_system_property('application/json')

        event.properties().add('deviceId', 'RaspberryPi3')

        if len(properties) > 0:
            prop_map = event.properties()
            for key in properties:
                prop_map.add_or_update(key, properties[key])

        self.client.send_event_async(
            event, send_confirmation_callback, send_context)

    def send_reported_state(self, reported_state, size, user_context):
        self.client.send_reported_state(
            reported_state, size,
            send_reported_state_callback, user_context)


def main(connection_string, protocol, pbi):
    global MESSAGE_COUNTER
    try:
        print("\nPython %s\n" % sys.version)
        print("IoT Hub Client for Python")

        hub_manager = HubManager(connection_string, protocol)

        print("Starting the IoT Hub Python sample using protocol {}..."
              .format(hub_manager.client_protocol))

        reported_state = "{\"newState\":\"standBy\"}"

        hub_manager.send_reported_state(
            reported_state, len(reported_state), 1002
        )

        while True:
            motion_sensor.wait_for_active(timeout=120)
            MESSAGE_COUNTER += 1

            if motion_sensor.value == 0:
                print("No motion sensed")
                hub_manager.send_event(
                    MSG_TXT %
                    (datetime.datetime.now(), 0, MESSAGE_COUNTER),
                    {}, MESSAGE_COUNTER
                )
                pbi.pub_something(
                        "my_channel",
                        MSG_TXT % (datetime.datetime.now(), 0, MESSAGE_COUNTER)
                )
            else:
                print("Motion detected")
                led.blink(n=2)
                buzzer.beep(n=1)
                hub_manager.send_event(
                    MSG_TXT %
                    (datetime.datetime.now(), 1, MESSAGE_COUNTER),
                    {}, MESSAGE_COUNTER
                )
                pbi.pub_something(
                    "my_channel",
                    MSG_TXT % (datetime.datetime.now(), 1, MESSAGE_COUNTER)
                )
                print(MSG_TXT % (datetime.datetime.now(), 1, MESSAGE_COUNTER))
                print("IoTHubClient.send_event_async accepted message "
                      "[%d] for transmission to IoT Hub." % MESSAGE_COUNTER)

            time.sleep(5)

    except IoTHubError as iothub_error:
        print("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print("IoTHubClient stopped")

if __name__ == '__main__':
    pbi = PowerBI()
    main(CONNECTION_STRING, PROTOCOL, pbi)
