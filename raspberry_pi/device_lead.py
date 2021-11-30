#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from gpiozero import LED
from time import sleep
import requests

INTERVAL = 3

# GPIO
led = LED(18)


def main():

    while True:

        # Set the LED state same as 'LED' tag of the meta data
        led_state = requests.get(
            'http://metadata.soracom.io/v1/subscriber.tags.LED').text

        if int(led_state) == 1:
            print("turn LED on")
            led.on()
        else:
            print("turn LED off")
            led.off()

        # Update lastUpdated
        datetime_jst = (datetime.now() +
                        timedelta(hours=9)).isoformat(timespec='seconds')
        headers = {'Content-Type': 'application/json'}
        payload = "[{\"tagName\": \"lastUpdated\", \"tagValue\": \"[JST] " + datetime_jst + "\"}]"
        res = requests.put("http://metadata.soracom.io/v1/subscriber/tags",
                           headers=headers, data=payload)

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
