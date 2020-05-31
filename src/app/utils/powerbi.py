# import requests
# import adal
import json
import os
from pubnub.exceptions import PubNubException
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from dotenv import load_dotenv
load_dotenv()


def publish_callback(result, status):
    print("Power BI - async Callback success")
    print("Power BI - publish timetoken: %d" % result.timetoken)
    pass


class PowerBI(object):
    def __init__(self):
        self.pnconfig = PNConfiguration()
        self.pnconfig.subscribe_key = os.getenv('pbi_subscribe_key')
        self.pnconfig.publish_key = os.getenv('pbi_publish_key')
        self.pnconfig.ssl = False
        self.pubnub = PubNub(self.pnconfig)

    def pub_something(self, channel, message):

        try:
            if len(self.pnconfig.publish_key) > 0:
                message = json.loads(message)
                self.pubnub.publish().channel(channel).message(message). \
                    pn_async(publish_callback)

        except PubNubException as e:
            print(str(e))

if __name__ == '__main__':
    pbi = PowerBI()
    token = pbi.pub_something()

