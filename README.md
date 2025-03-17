# Trilobot Controls

## Update: install process has changed

Installing some Raspberry Pi modules doesn't seem as straightforward anymore after an update to Raspbian. In the past, modules were installed system-wide with `sudo` but now require a virtual environment. This is the best explanation I could find online: <https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3>

So now do this. Start by creating yourself a new venv.

`python -m venv ./trilobot_env`

Then activate the venv so that it becomes your active Python environment, where pip will install packages.

`source ./trilobot_env/bin/activate`

You should now see `(trilobot_env)` next to your username on the command line. Next, install all the packages you need.

`pip install trilobot RPi.GPIO gpiozero pigpio`

Finally, you need to activate and enable a PGIO service.

`sudo apt install pigpio && sudo pigpiod && sudo systemctl enable pigpiod`

Now you'll be all set to use the first example control below. Install any other dependency as required.

## Three examples of controls

I've split the three examples apart

* Really basic [console controls](./ssh/) that can be used over SSH
* A [PyQt GUI](./pyqt/) that communicates from a desktop PC to an API on the Trilobot
* A [web server](./web_gui/) that offers desktop and mobile controls on a local website

## Sample

![A screenshot of the desktop GUI](./web_gui/screenshot.png)

## ~~Cat~~ Robot tax

![A ferocious feline relaxing next to its treat robot](./cat_tax.jpg)
