import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
import numpy as np

import motor
import pigpio
from gpiozero import Motor
import time
from threading import Thread








if __name__ == "__main__":
        
    motor.setup()

    run = int(input('出力調整はいくつ'))
    while 1:
        
        # print('----------------')
        # old = acc.acc_dataRead()
        # print(f'old {old}')
        # motor.motor_move(30, 30, n)
        # new = acc.acc_dataRead()
        # print(f'new {new}')
        a = input('入力')
        if a == 'w':
            motor.motor_continue(30,30)
        elif a == 'a':
            motor.motor_continue(30 - run,30 + run)
        elif a == 'd':
            motor.motor_continue(30 + run,30 - run)
        elif a == 's':
            motor.motor_continue(-30,-30)
    
    
    