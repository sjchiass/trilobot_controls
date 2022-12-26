from fastapi import FastAPI, Path, Query, BackgroundTasks
from fastapi.responses import Response
import asyncio
from time import sleep
from trilobot import Trilobot
from datetime import datetime, timedelta
from time import sleep
from brightpi import *

brightPi = BrightPi()
# This method is used to reset the SC620 to its original state.
brightPi.reset()
#brightPi.set_gain(0)

from PIL import Image
import io
import json
from picamera2 import Picamera2
picam2 = Picamera2()

preview_config = picam2.create_preview_configuration(main={"size": (800, 600)},
    controls={"FrameDurationLimits": (100000, 10000)})
picam2.configure(preview_config)

picam2.start()

app = FastAPI()
tbot = Trilobot()
tbot.servo_to_center()

class BackgroundRunner:
    def __init__(self):
        self.deadman_switch = datetime.now()

    async def run_main(self):
        while True:
            await asyncio.sleep(2)
            if datetime.now() > self.deadman_switch:
                tbot.coast()
            else:
                pass

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/commands/lights_rgb")
async def lights(red: int = 0, green: int = 0, blue: int = 0):
    tbot.fill_underlighting(red, green, blue)
    return {"message": "Lights at {red} {green} {blue}"}

@app.get("/commands/lights_on")
async def lights_on():
    tbot.fill_underlighting(255, 255, 255)
    return {"message": "Lights on"}

@app.get("/commands/lights_off")
async def lights_off():
    tbot.fill_underlighting(0, 0, 0)
    return {"message": "Lights off"}

@app.get("/commands/drive")
async def drive(
    background_tasks: BackgroundTasks,
    left: float = Query(default=0.0, ge=-1.0, le=1.0),
    right: float = Query(default=0.0, ge=-1.0, le=1.0)):
        tbot.set_motor_speeds(left, right)
        runner.deadman_switch = datetime.now() + timedelta(seconds = 2)
        return {"message": f"Driving {left} {right}"}

@app.get("/commands/servo")
async def drive(
    angle: float = Query(default=0.5, ge=0.0, le=1.0)):
	    # I had to play with this a bit since the servo can't go beyond 60%
        tbot.servo_to_percent(min(max(angle, 0.05), 0.60))
        return {"message": f"Setting servo to {angle}"}

@app.get("/commands/coast")
async def coast():
    tbot.coast()
    return {"message": f"Coasting"}

@app.get("/commands/ultrasonic")
async def ultrasonic():
    return {"message": tbot.read_distance()}

@app.get("/commands/headlights_on")
async def headlights_on():
    brightPi.set_led_on_off(LED_ALL[0:3], ON)

@app.get("/commands/headlights_off")
async def headlights_off():
    brightPi.set_led_on_off(LED_ALL[0:3], OFF)

@app.get("/commands/ir_headlights_on")
async def ir_headlights_on():
    brightPi.set_led_on_off(LED_ALL[4:8], ON)

@app.get("/commands/ir_headlights_off")
async def ir_headlights_off():
    brightPi.set_led_on_off(LED_ALL[4:8], OFF)

@app.get("/commands/nightmode_on")
async def nightmode_on():
    picam2.set_controls({"Brightness": 1.0, "Contrast": 3.0, "Saturation": 0.0})

@app.get("/commands/nightmode_off")
async def nightmode_off():
    picam2.set_controls({"Brightness": 0.0, "Contrast": 1.0, "Saturation": 1.0})

@app.get("/commands/capture_camera")
async def capture_camera():
    arr = picam2.capture_array()
    im = Image.fromarray(arr)
    
    # save image to an in-memory bytes buffer
    with io.BytesIO() as buf:
        im.convert('RGB').save(buf, format='JPEG', quality=50)
        im_bytes = buf.getvalue()
        
    headers = {'Content-Disposition': 'inline; filename="feed.jpeg"'}
    return Response(im_bytes, headers=headers, media_type='image/jpeg')

@app.get("/checkin")
async def checkin():
    runner.deadman_switch = datetime.now() + timedelta(seconds = 1)
