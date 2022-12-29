# Web controls for Trilobot

## Overview

This code starts servers on the Trilobot that you can connect to with your desktop or mobile web browser.

A FastAPI server handles commands to the Trilobot while [a vanilla picamera2 mjpg server](https://github.com/raspberrypi/picamera2/blob/main/examples/mjpeg_server.py) streams the camera.

The **`start.py`** script starts both of these as subprocesses. You can then point your browser to the address it gives. (The IP address it gives is not always correct, so use `ifconfig` in the terminal to figure out what the Trilobot's IP address really is. The GUI always runs on port 8000.)

I am not very good at javascript so I had to use [this W3Schools guide](https://www.w3schools.com/graphics/game_controllers.asp) to make keyboard controls. For the mobile controls I used [this Joystick Project code](https://github.com/bobboteck/JoyStick).

## Installation

You can install everything with

```console
pip3 install fastapi picamera2 trilobot
```

* [FastAPI](https://pypi.org/project/fastapi/) runs Python code in response to web requests, ex: `http://server:8000/commands/drive?left=1.0&right=1.0`
* [trilobot](https://github.com/pimoroni/trilobot-python) is the interface between Python and the Trilobot hardware
* [picamera2](https://github.com/raspberrypi/picamera2) is the interface between Python and the picamera

## Sample

![A screenshot of the desktop GUI](screenshot.png)