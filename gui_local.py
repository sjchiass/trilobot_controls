import sys
from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QFont
import requests
import time
import json
import numpy as np
import argparse

parser = argparse.ArgumentParser(
    description="Control a robot API")
parser.add_argument("api_address", type=str, help="Address of API server, something like https://192.168.0.1:8000/")

args = parser.parse_args()


class UltrasonicWorker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(str)

    @pyqtSlot()
    def procCounter(self): # A slot takes no params
        while True:
            time.sleep(1)
            response = requests.get(f'{args.api_address}commands/ultrasonic').text
            range_value = json.loads(response)["message"]
            if range_value != -999:
                self.intReady.emit(f"{range_value:6.2f}cm")

        self.finished.emit()

class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        while True:
            time.sleep(0.1)
            data = requests.get(f"{args.api_address}commands/capture_camera").content
            image = QImage()
            image.loadFromData(data)
            self.changePixmap.emit(image)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Vertical, meaning the top and bottom halves of the GUI
        v_layout = QVBoxLayout()
        
        # The top half of the GUI with motor controls and the camera feed
        h1_layout = QHBoxLayout()
        
        # The bottom half of the GUI with servo and light controls.
        # Also has the ultrasonic sensor reading
        h2_layout = QHBoxLayout()
        
        # ---
        # The grid of buttons to control the robot's movement
        # The buttons are controlled by a keyboard's numpad
        movement_group = QGroupBox("Motor control")
        movement_grid = QGridLayout()

        # A list of all the buttons
        self.move_buttons = [""]
        
        # The integer IDs of the movement keys, with 0 being blank so
        # that move_keys[1] gives 49 (1) and so on
        self.move_keys = ["", 49, 50, 51, 52, 53, 54, 55, 56, 57]

        # Create all of the buttons and set them in the grid
        for i in range(1, 10):
            self.move_buttons.append(QPushButton(str(i)))
            self.move_buttons[-1].setCheckable(True)
            self.move_buttons[-1].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            movement_grid.addWidget(self.move_buttons[-1], 2-(i-1)//3, (i-1)%3)
        
        # Set the controls into the layout
        movement_group.setLayout(movement_grid)
        h1_layout.addWidget(movement_group)
        
        # ---
        # Slider for overall motor speed
        speed_group = QGroupBox("Motor power level")
        speed_layout = QVBoxLayout()
        speed_group.setLayout(speed_layout)
        h1_layout.addWidget(speed_group)
        
        # The overall motor speed slider is in percentage of maximum 100%
        # power, in 10% increments. PyQt stores these values in integers
        # of 0 to 10, which are divided by 10 to give percentages.
        self.speed_label = QLabel("80%")
        self.speed_label.setAlignment(Qt.AlignCenter)
        speed_layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Orientation.Vertical)
        self.speed_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setSingleStep(1)
        self.speed_slider.setPageStep(1)
        self.speed_slider.setTickPosition(1)
        self.speed_slider.setValue(8)      
        self.speed_slider.valueChanged.connect(self.speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        # ---
        # Slider for motor power balance, meaning how to split power
        # between the left and right motors.
        motor_balance_group = QGroupBox("Motor power ratio")
        motor_balance_layout = QVBoxLayout()
        motor_balance_group.setLayout(motor_balance_layout)
        h1_layout.addWidget(motor_balance_group)
        
        # The controls are values of 0 to 50, split into two halves.
        # The raw value is divided by 50 and then has 0.5 subtracted from
        # it. This gives negative and positive values to offset left
        # motor against right.
        self.motor_balance_label = QLabel("1:1")
        self.motor_balance_label.setAlignment(Qt.AlignCenter)
        motor_balance_layout.addWidget(self.motor_balance_label)
        self.motor_balance = QSlider(Qt.Orientation.Vertical)
        self.motor_balance.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.motor_balance.setMinimum(0)
        self.motor_balance.setMaximum(50)
        self.motor_balance.setTickInterval(1)
        self.motor_balance.setSingleStep(1)
        self.motor_balance.setPageStep(1)
        self.motor_balance.setTickPosition(1)
        self.motor_balance.setValue(25)
        self.motor_balance.valueChanged.connect(self.motor_balance_changed)
        motor_balance_layout.addWidget(self.motor_balance)
        
        # ---
        # Non-functional sliders only meant to show the user how much
        # power is given to each motor. Depending on the values of the
        # other controls, the power sent to the motors can change a lot.
        motor_indicator_group = QGroupBox("Motor current power")
        motor_indicator_layout = QHBoxLayout()
        motor_indicator_group.setLayout(motor_indicator_layout)
        h1_layout.addWidget(motor_indicator_group)
        
        self.left_motor_slider = QSlider(Qt.Orientation.Vertical)
        self.right_motor_slider = QSlider(Qt.Orientation.Vertical)
        self.left_motor_label = QLabel(" 0.00")
        self.right_motor_label = QLabel(" 0.00")
        self.left_motor_slider.setValue(50)
        self.right_motor_slider.setValue(50)
        motor_indicator_layout.addWidget(self.left_motor_label)
        motor_indicator_layout.addWidget(self.left_motor_slider)
        motor_indicator_layout.addWidget(self.right_motor_slider)
        motor_indicator_layout.addWidget(self.right_motor_label)
        
        # ---
        # The camera feed as a frequently-refreshing image display
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)
        h1_layout.addWidget(self.label)
        
        th = CameraThread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        
        # ---
        # The cheap hobby servo can rotate 180 degrees. The slider here
        # only allows three positions, to simplify things. The servo is
        # meant to toss cat treats.
        servo_group = QGroupBox("Servo position")
        servo_layout = QVBoxLayout()
        servo_group.setLayout(servo_layout)
        h2_layout.addWidget(servo_group)
        
        self.servo_slider = QSlider(Qt.Orientation.Horizontal)
        self.servo_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.servo_slider.setMinimum(0)
        self.servo_slider.setValue(1)
        self.servo_slider.setMaximum(2)
        self.servo_slider.setTickInterval(1)
        self.servo_slider.setSingleStep(1)
        self.servo_slider.setPageStep(1)
        self.servo_slider.setTickPosition(1)
        self.servo_slider.valueChanged.connect(self.servo_slider_changed)
        servo_layout.addWidget(self.servo_slider)
        
        # ---
        # The Trilobot has RGB LEDs underneath its chassis. Their RGB
        # color channels can be controlled separately, so the sliders
        # here can be each set between 0 and 255.
        rgb_group = QGroupBox("RGB controls")
        rbg_layout = QVBoxLayout()
        rgb_group.setLayout(rbg_layout)
        h2_layout.addWidget(rgb_group)
        
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setMinimum(0)
        self.r_slider.setValue(0)
        self.r_slider.setMaximum(255)
        self.g_slider = QSlider(Qt.Orientation.Horizontal)
        self.g_slider.setMinimum(0)
        self.g_slider.setValue(0)
        self.g_slider.setMaximum(255)
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setMinimum(0)
        self.b_slider.setValue(0)
        self.b_slider.setMaximum(255)
        rbg_layout.addWidget(QLabel("Red"))
        rbg_layout.addWidget(self.r_slider)
        rbg_layout.addWidget(QLabel("Green"))
        rbg_layout.addWidget(self.g_slider)
        rbg_layout.addWidget(QLabel("Blue"))
        rbg_layout.addWidget(self.b_slider)
        self.r_slider.valueChanged.connect(self.rgb_slider_changed)
        self.g_slider.valueChanged.connect(self.rgb_slider_changed)
        self.b_slider.valueChanged.connect(self.rgb_slider_changed)
        
        # ---
        # The BrightPi can do a lot with its LEDs, but the only two settings
        # here are full-on visible-light white LEDs and full-on infrared
        # LEDs. The third button toggles the camera between its default
        # mode and a high-contrast grayscale more, for night vision.
        light_group = QGroupBox("Light controls")
        light_layout = QVBoxLayout()
        light_group.setLayout(light_layout)
        h2_layout.addWidget(light_group)
        
        # Visible-light headlights
        self.headlights = QPushButton("Headlights")
        self.headlights.setCheckable(True)
        self.headlights.clicked.connect(self.headlights_changed)
        light_layout.addWidget(self.headlights)
        
        # Infrared headlights
        self.ir_headlights = QPushButton("IR Headlights")
        self.ir_headlights.setCheckable(True)
        self.ir_headlights.clicked.connect(self.ir_headlights_changed)
        light_layout.addWidget(self.ir_headlights)
        
        # Nightvision mode for camera
        self.high_visibility = QPushButton("High visibility")
        self.high_visibility.setCheckable(True)
        self.high_visibility.clicked.connect(self.high_visibility_changed)
        light_layout.addWidget(self.high_visibility)
        
        # ---
        # This is the background thread for rangefinder readout
        self.range = QLabel("0")
        range_font = QFont()
        range_font.setPointSize(18)
        self.range.setFont(range_font)
        
        self.obj = UltrasonicWorker()
        self.thread = QThread()
        self.obj.intReady.connect(self.onIntReady)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.procCounter)
        self.thread.start()

        # Distance readout, a label that displays distance in cms
        range_group = QGroupBox("Ultrasonic distance")
        range_layout = QVBoxLayout()
        range_layout.addWidget(self.range)
        range_group.setLayout(range_layout)
        h2_layout.addWidget(range_group)
        
        #Layout
        v_layout.addLayout(h1_layout)
        v_layout.addLayout(h2_layout)
        self.setLayout(v_layout)
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
    
    def onIntReady(self, i):
        self.range.setText(f"{i}")
    
    def speed_changed(self, event):
        self.speed_label.setText(f"{self.speed_slider.value()*10}%")
    
    def motor_balance_changed(self, event):
        left_adj = 1.0 - max(0, self.motor_balance.value()/50.0 - 0.5)
        right_adj = 1.0 - max(0, 0.5 - self.motor_balance.value()/50.0)
        self.motor_balance_label.setText(f"{left_adj}:{right_adj}")
    
    def servo_slider_changed(self, event):
        requests.get(f"{args.api_address}commands/servo?angle={event/2}")
        print(f"{args.api_address}commands/servo?angle={event/2}")
    
    def rgb_slider_changed(self, event):
        r = self.r_slider.value()
        g = self.g_slider.value()
        b = self.b_slider.value()
        requests.get(f"{args.api_address}commands/lights_rgb?red={r}&green={g}&blue={b}")
        print(f"{args.api_address}commands/lights_rgb?red={r}&green={g}&blue={b}")
    
    def headlights_changed(self, event):
        if self.headlights.isChecked():
            requests.get(f"{args.api_address}commands/headlights_on")
        else:
            requests.get(f"{args.api_address}commands/headlights_off")
    
    def ir_headlights_changed(self, event):
        if self.ir_headlights.isChecked():
            requests.get(f"{args.api_address}commands/ir_headlights_on")
        else:
            requests.get(f"{args.api_address}commands/ir_headlights_off")
    
    def high_visibility_changed(self, event):
        if self.high_visibility.isChecked():
            requests.get(f"{args.api_address}commands/nightmode_on")
        else:
            requests.get(f"{args.api_address}commands/nightmode_off")
    
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            #requests.get(f"{args.api_address}checkin")
            return
        print("press"+str(event.key()))
        if event.key() in self.move_keys:
            for i in range(1, 10):
                if event.key() == self.move_keys[i]:
                    self.move_buttons[i].setChecked(True)
                    self.send_commands()
        elif event.key() == 43:
            self.speed_slider.setValue(self.speed_slider.value()+1)
        elif event.key() == 45:
            self.speed_slider.setValue(self.speed_slider.value()-1)
        elif event.key() == 47:
            self.servo_slider.setValue(self.servo_slider.value()-1)
        elif event.key() == 42:
            self.servo_slider.setValue(self.servo_slider.value()+1)
        elif event.key() == 48:
            print(requests.get(f"{args.api_address}commands/ultrasonic").text)
        
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        print("release"+str(event.key()))
        if event.key() in self.move_keys:
            for i in range(1, 10):
                if event.key() == self.move_keys[i]:
                    self.move_buttons[i].setChecked(False)
                    self.send_commands()
    
    def send_commands(self):
        speed = self.speed_slider.value()/10.0
        left_adj = 1.0 - max(0, self.motor_balance.value()/50.0 - 0.5)
        right_adj = 1.0 - max(0, 0.5 - self.motor_balance.value()/50.0)
        left = 0
        right = 0
        concurrent = sum([self.move_buttons[i].isChecked() for i in range(1, 10)])
        print(concurrent)
        if concurrent:
            if self.move_buttons[1].isChecked():
                left += -0.7*speed
                right += -speed
            if self.move_buttons[2].isChecked():
                left += -speed
                right += -speed
            if self.move_buttons[3].isChecked():
                left += -speed
                right += -0.7*speed
            if self.move_buttons[4].isChecked():
                left += -0.7*speed
                right += 0.7*speed
            if self.move_buttons[5].isChecked():
                pass
            if self.move_buttons[6].isChecked():
                left += 0.7*speed
                right += -0.7*speed
            if self.move_buttons[7].isChecked():
                left += 0.7*speed
                right += speed
            if self.move_buttons[8].isChecked():
                left += speed
                right += speed
            if self.move_buttons[9].isChecked():
                left += speed
                right += 0.7*speed
            left = left_adj*left/concurrent
            right = right_adj*right/concurrent
            self.left_motor_label.setText(f"{left:5.2f}")
            self.left_motor_slider.setValue(int(50+50*left))
            self.right_motor_slider.setValue(int(50+50*right))
            self.right_motor_label.setText(f"{right:5.2f}")
            requests.get(f"{args.api_address}commands/drive?left={left}&right={right}")
        else:
            requests.get(f"{args.api_address}commands/coast")
            self.left_motor_label.setText(" 0.00")
            self.left_motor_slider.setValue(50)
            self.right_motor_slider.setValue(50)
            self.right_motor_label.setText(" 0.00")
        print(f"{args.api_address}commands/drive?left={left}&right={right}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = MainWindow()
    demo.show()

    sys.exit(app.exec_())
