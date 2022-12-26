#
# API server for Trilobot
#
# Copy this file to your RPi, `cd` to its directory, and then
# run this on your RPi with uvicorn fastapi_remote:app --host 0.0.0.0
#
# Standard libraries
from time import sleep
from datetime import datetime, timedelta
from time import sleep
import io

# Extra libraries
import asyncio
from fastapi import FastAPI, Path, Query, BackgroundTasks
from fastapi.responses import Response
from PIL import Image
from trilobot import Trilobot

# Extra optional library: BrightPi LED array
def activate_brightpi():
    from brightpi import BrightPi
    global BRIGHTPI
    BRIGHTPI = BrightPi()
    # This method is used to reset the SC620 to its original state.
    BRIGHTPI.reset()
    #brightPi.set_gain(0)

# Extra optional library: Picamera2 for remote viewing
def activate_picam2():
    from picamera2 import Picamera2
    global PICAM2
    PICAM2 = Picamera2()
    preview_config = PICAM2.create_preview_configuration(main={"size": (800, 600)},
        controls={"FrameDurationLimits": (100000, 10000)})
    PICAM2.configure(preview_config)
    PICAM2.start()

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
    if "BRIGHTPI" not in globals():
        activate_brightpi()
    BRIGHTPI.set_led_on_off((1, 2, 3, 4), 1)

@app.get("/commands/headlights_off")
async def headlights_off():
    if "BRIGHTPI" not in globals():
        activate_brightpi()
    BRIGHTPI.set_led_on_off((1, 2, 3, 4), 0)

@app.get("/commands/ir_headlights_on")
async def ir_headlights_on():
    if "BRIGHTPI" not in globals():
        activate_brightpi()
    BRIGHTPI.set_led_on_off((5, 6, 7, 8), 1)

@app.get("/commands/ir_headlights_off")
async def ir_headlights_off():
    if "BRIGHTPI" not in globals():
        activate_brightpi()
    BRIGHTPI.set_led_on_off((5, 6, 7, 8), 0)

@app.get("/commands/nightmode_on")
async def nightmode_on():
    if "PICAM2" not in globals():
        activate_picam2()
    PICAM2.set_controls({"Brightness": 1.0, "Contrast": 3.0, "Saturation": 0.0})

@app.get("/commands/nightmode_off")
async def nightmode_off():
    if "PICAM2" not in globals():
        activate_picam2()
    PICAM2.set_controls({"Brightness": 0.0, "Contrast": 1.0, "Saturation": 1.0})

@app.get("/commands/capture_camera")
async def capture_camera():
    if "PICAM2" not in globals():
        activate_picam2()
    arr = PICAM2.capture_array()
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
