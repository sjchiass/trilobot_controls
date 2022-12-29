import sys
import select
import tty
import termios
from time import sleep
from trilobot import Trilobot

tbot = Trilobot()
tbot.servo_to_center()

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)

def tbot_dispatch(i, speed):
    if i in ["w", "a", "s", "d", "q", "e"]:
        if i == "w":
            tbot.forward(speed)
        elif i == "a":
            tbot.turn_left(0.8*speed)
        elif i == "s":
            tbot.backward(speed)
        elif i == "d":
            tbot.turn_right(0.8*speed)
        elif i == "q":
            tbot.set_motor_speeds(0.8*speed, speed)
        elif i == "e":
            tbot.set_motor_speeds(speed, 0.8*speed)
    elif i in ["c", "v", "b", "n", "m"]:
        if i == "c":
            tbot.servo_to_percent(0.05)
        elif i == "v":
            tbot.servo_to_percent(0.25)
        elif i == "b":
            tbot.servo_to_percent(0.5)
        elif i == "n":
            tbot.servo_to_percent(0.75)
        elif i == "m":
            tbot.servo_to_percent(0.95)
    elif i == "l":
        tbot.fill_underlighting(255, 255, 255)
    elif i == "k":
        tbot.fill_underlighting(0, 0, 0)
    elif i in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
        i = float(i)
        if i == 0.0:
            speed = 1.0
        else:
            speed = i/10.0
    else:
        tbot.coast()
    # Return the speed value
    return speed

speed = 0.5
downtime = 0
increment = 0.05
threshold = 10 * 0.05
at_rest = False
new, old = "", ""
try:
    tty.setcbreak(sys.stdin.fileno())

    while True:
        if isData():
            new = sys.stdin.read(1)
            at_rest = False
            downtime = 0
            if new == '\x1b':         # x1b is ESC
                break
            elif new != old:
                speed = tbot_dispatch(new, speed)
            old = new
        else:
            if at_rest:
                pass
            else:
                if downtime > threshold:
                    at_rest = True
                    new, old = "", ""
                    tbot.coast()
                    print("AT REST")
                else:
                    downtime += increment
                    sleep(increment)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
