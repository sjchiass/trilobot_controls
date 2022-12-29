# Basic SSH controls

## Overview

Suppose you just want to SSH into your Trilobot and control it with your keyboard. Just copy this script over, run it remotely, and you'll be able to move your Trilobot around.

## Installation

Just copy the file over to the Trilobot/RPi and then run it from there while logged in through SSH. Alternatively you can use it directly if you have a keyboard and screen connected to the Trilobot.

No extra Python packages required.

## Usage

Here's what each key does

* **W** forward
* **A** rotate left
* **S** backwards
* **D** rotate right
* **Q** curve left
* **E** curve right

* **C, V, B, N, M** operate servo from min to max

* **L** chassis lights to on
* **K** cassis lights to off

* **1, 2, 3, .., 9, 0** set motor power to 10%, 20%, 30%, .., 90%, 100%
