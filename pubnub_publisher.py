
import os
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.enums import PNOperationType

def publish_to_pubnub(id_list, park_list, channel):
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.getenv('PN_SUBSCRIBEKEY')
    pnconfig.publish_key = os.getenv('PN_PUBLISHKEY')
    pnconfig.user_id = 'parktesting'
    pubnub = PubNub(pnconfig)

    data = {'id_list': id_list, 'boolean_values': park_list}

    def publish_callback(result, status):
        if status.is_error():
            print(f"Error publishing message: {status.error_data}")
            print(status.status_code)
        else:
            print("Message published successfully")
            print(result.timetoken)

    pubnub.publish().channel(channel).message(data).pn_async(publish_callback)