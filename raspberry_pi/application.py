#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from gpiozero import LED
from time import sleep
import json
import threading
import os
import sys

led = LED(18)

thing_name = "raspberry-pi"
shadow_topic_prefix = "$aws/things/" + thing_name + "/shadow/name/led"
INTERVAL = 60


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(shadow_topic_prefix + "/get/accepted")
    client.subscribe(shadow_topic_prefix + "/update/delta")


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    payload = json.loads(msg.payload)

    if msg.topic == shadow_topic_prefix + "/get/accepted":
        if payload.get("state", {}).get("reported"):
            set_led(payload["state"]["reported"].get("led"))
            print("run report thread to fit the state to reported")
            report = threading.Thread(target=report_shadow)
            report.start()
        else:
            print("nothing reported yet")

        if payload.get("state", {}).get("delta"):
            print("There is delta! (/get/accepted)")
            set_led(payload["state"]["delta"].get("led"))
            print("run report thread to fit the state to delta")
            report = threading.Thread(target=report_shadow)
            report.start()
        else:
            print("no delta")
    elif msg.topic == shadow_topic_prefix + "/update/delta":
        print("There is delta! (/update/delta)")
        set_led(payload["state"].get("led"))
        print("run report thread to fit the state to delta")
        report = threading.Thread(target=report_shadow)
        report.start()
    else:
        print("unknown topic")


def set_led(led_state):
    if led_state == "1":
        led.on()
    else:
        led.off()
    if str(led.value) != led_state:
        print("Something wrong. Restart the process.")
        os.execl(sys.executable, 'python3', __file__)
    return


def report_shadow():
    message = {"state": {"reported": {"led": str(led.value)}}}
    print("report! message is " + str(message))
    client.publish(shadow_topic_prefix + "/update", json.dumps(message))


def get_shadow():
    client.publish(shadow_topic_prefix + "/get", "")


def subscribing():
    client.on_message = on_message
    client.loop_forever()


if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.connect("beam.soracom.io", 1883, 60)
    sub = threading.Thread(target=subscribing)
    sub.start()
    sleep(0.5)
    while True:
        print("Get the shadow")
        get_shadow()
        sleep(INTERVAL)
