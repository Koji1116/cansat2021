import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Casnat2021ver/detection')
import numpy as np
import BMC050
import acc
import time
from threading import Thread
import stuck



BMC050.bmc050_setup()
while 1:
    za = []
    for i in range(3):
        accdata = acc.acc_dataread()
        za.append(accdata[2])
        time.sleep(0.2)
    z = max(za)
    print(z)