#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request
from gpiozero import LED

led = LED(18)

app = Flask(__name__)


@app.route("/")
# curl http://127.0.0.1:5000/
def get_led_state():
    return str(led.value)


@app.route("/led", methods=['PUT'])
# curl -X PUT -H "Content-type: application/json" -d '{"led":1}' http://127.0.0.1:5000/led
def update_led_state():
    new_led_state = request.get_json()["led"]

    if (int(new_led_state)):
        print("turn the LED on")
        led.on()
    else:
        print("turn the LED off")
        led.off()

    return "200 OK"


if __name__ == "__main__":
    app.run("0.0.0.0")
