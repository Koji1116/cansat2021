import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/envirionmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/illuminance')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
import melt
import BME280
import Xbee
import mag
import GPS
import TSL2572
#import acc 
import Xbee
from gpiozero import Motor
import time
import motor
from smbus import SMBus
import pigpio
import picamera
import Capture
import os

pi = pigpio.pi()

meltPin  = 17
camerapath = '/home/pi/Desktop/Cansat2021ver/test/img_falltest/falltest'

##### for only acc
ACC_ADDRESS = 0x19
ACC_REGISTER_ADDRESS = 0x02
i2c = SMBus(1)

def bmc050_setup():
    # --- BMC050Setup --- #
    # Initialize ACC
    try:
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)
    except:
        time.sleep(0.1)
        print("BMC050 Setup Error")
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)

def acc_dataRead():
    # --- Read Acc Data --- #
    accData = [0, 0, 0, 0, 0, 0]
    value = [0.0, 0.0, 0.0]
    for i in range(6):
        try:
            accData[i] = i2c.read_byte_data(
                ACC_ADDRESS, ACC_REGISTER_ADDRESS+i)
        except:
            pass
            # print("error")

    for i in range(3):
        value[i] = (accData[2*i+1] * 16) + (int(accData[2*i] & 0xF0) / 16)
        value[i] = value[i] if value[i] < 2048 else value[i] - 4096
        value[i] = value[i] * 0.0098 * 1

    return value

print('----i2cdetect----')
os.system('i2cdetect -y 1')

print('\n----camera----')
os.system('vcgencmd get_camera')
try:
    Capture.Capture(camerapath)
except:
    print('error : camera\n')

print('\n---Environment---')
try:
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    for _ in range(5):
        bme_data = BME280.bme280_read()
        print(bme_data)
        time.sleep(1)
except:
    print('error : env')


# print('---melt----')
# try:
# 	melt.down()
# except:
# 	pi.write(meltPin, 0)




print('---motor---')
motor.setup()
motor.move(20,20,2)




print('---mag---')
try:
    mag.bmc050_setup()
    for _ in range(5):
        mag_data = mag.mag_dataread()
        print(mag_data)
        time.sleep(0.2)
except:
    print('error : mag')
 
print('---acc---')
try:
    bmc050_setup()
    for _ in range(5):
        acc_data = acc_dataRead()
        print(acc_data)
        time.sleep(0.2)
except:
    print('error : acc')







# print('---illuminance---')
# try:
#     for _ in range(5):
#         ill_data = TSL2572.main()
#         print(ill_data)
# except:
#     print('error : TSL2572')

print('---Xbee---')
try:
    Xbee.on()
    for i in range(10):
        Xbee.str_trans(str(i)+'  : reseive?')
except:
    print('error : Xbee')

print('---gps---')
try:
    GPS.openGPS()
    data = GPS.GPSdata_read()
    print(data)
except:
    print('error : gps')



