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
import asyncio

# Extra libraries
from PIL import Image
from trilobot import Trilobot
from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


tbot = Trilobot()
tbot.servo_to_center()


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
        left: float = Query(default=0.0, ge=-1.0, le=1.0),
        right: float = Query(default=0.0, ge=-1.0, le=1.0)):
    tbot.set_motor_speeds(left, right)
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
    return f"{tbot.read_distance():3.0f}cm"

# The javascript for controlling the bot comes from here:
# https://www.w3schools.com/graphics/game_controllers.asp


@app.get("/")
def render_controls(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
