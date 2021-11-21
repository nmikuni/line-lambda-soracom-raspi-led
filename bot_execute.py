import os
import json
import logging
import subprocess
import boto3
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
soracom_auth_key_id = os.getenv('SORACOM_AUTH_KEY_ID')
soracom_auth_key = os.getenv('SORACOM_AUTH_KEY')
soracom_sim_id = os.getenv('SIM_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# LineBotAPI
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
sqs = boto3.client('sqs')
queue_url = os.getenv('QUEUE_URL')

# SORACOM API
soracom_common_arg = ' --auth-key-id ' + \
    soracom_auth_key_id + ' --auth-key ' + soracom_auth_key


# Lambda Response
ok_response = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
}
error_response = {
    "isBase64Encoded": False,
    "statusCode": 401,
    "headers": {},
    "body": ""
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_text = event.message.text
    print(message_text)

    if (message_text == "電気ついてる？"):
        return_message_text = get_led_check_message(get_sim_tags())
    elif (message_text == "電気つけて"):
        set_led("1")
        return_message_text = "つけるね"
    elif (message_text == "電気消して"):
        set_led("0")
        return_message_text = "消すね"
    else:
        print("fuga")
        return_message_text = "メニュー中のボタンを押してね"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(return_message_text)
    )


def get_sim_tags():
    soracom_cli_get_sim = "soracom sims get --sim-id " + \
        soracom_sim_id + soracom_common_arg
    sim_info = json.loads((subprocess.run(
        soracom_cli_get_sim, shell=True, stdout=subprocess.PIPE)).stdout.decode())
    # tags = {"LED":"1","lastUpdated":"[JST] 2021-11-20T23:43","name":"RasPi-vSIM"}
    return sim_info['tags']


def get_led_check_message(tags):
    led_state = int(tags['LED'])
    last_updated = tags['lastUpdated']

    led_state_message = 'ついてるよ' if (led_state) else '消えてるよ'
    ret_message = led_state_message + "\n最終更新: " + last_updated
    return ret_message


def set_led(led_state):
    soracom_cli_put_sim_tags = "soracom sims put-tags --sim-id " + \
        soracom_sim_id + \
        ' --body \'[{"tagName":"LED","tagValue":"' + \
        led_state + '"}]\'' + soracom_common_arg
    print(soracom_cli_put_sim_tags)
    subprocess.run(soracom_cli_put_sim_tags,
                   shell=True, stdout=subprocess.PIPE)
    return


def lambda_handler(event, context):
    print(event)
    try:
        for record in event['Records']:
            record_body = json.loads(record['body'])
            signature = record_body["headers"]["x-line-signature"]
            event_body = record_body['body']
        handler.handle(event_body, signature)
    except InvalidSignatureError as e:
        logger.error(e)
        return error_response
    except Exception as e:
        logger.error(e)
        return error_response
    return ok_response
