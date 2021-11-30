import os
import json
import logging
import boto3
import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# LineBotAPI
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
sqs = boto3.client('sqs')
queue_url = os.getenv('QUEUE_URL')

# AWS IoT
endpoint_url = os.getenv('AWS_IOT_ENDPOINT_URL')
thing_name = os.getenv('AWS_IOT_THING_NAME')

client = boto3.client(
    'iot-data', endpoint_url=endpoint_url)

response = client.get_thing_shadow(
    thingName=thing_name,
    shadowName='led'
)

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
    logger.info("message is " + message_text)

    try:
        if (message_text == "電気ついてる？"):
            return_message_text = get_led_check_message()
        elif (message_text == "電気つけて"):
            set_led("1")
            return_message_text = "つけるね"
        elif (message_text == "電気消して"):
            set_led("0")
            return_message_text = "消すね"
        else:
            logger.warn("Invalid input")
            return_message_text = "メニュー中のボタンを押してね"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(return_message_text)
        )
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("エラーだよ")
        )


def get_led_check_message():
    response = client.get_thing_shadow(
        thingName=thing_name,
        shadowName='led'
    )

    payload = json.loads(response["payload"].read().decode())

    led_state = payload["state"].get("reported", {}).get("led")
    timestamp_jst = payload["timestamp"] + 32400
    last_updated = str(datetime.datetime.fromtimestamp(timestamp_jst))

    led_state_message = 'ついてるよ' if (int(led_state)) else '消えてるよ'
    ret_message = led_state_message + "\n最終更新 [JST]: " + last_updated
    return ret_message


def set_led(led_state):
    shadowDoc = {'state': {'desired': {'led': led_state}}}
    new_payload = bytes(json.dumps(shadowDoc), "utf-8")

    res = client.update_thing_shadow(
        thingName=thing_name, shadowName='led', payload=new_payload)

    return


def lambda_handler(event, context):
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
