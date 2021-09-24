import os
import time
from smbus import SMBus
import pigpio

from sensor.envirionmental import bme280
from sensor.axis import mag
from sensor.gps import gps
from sensor.communication import xbee
import motor
from sensor.camera import take

pi = pigpio.pi()

meltPin = 17
camerapath = '/home/pi/Desktop/cansat2021/photostrage/sensor_test'

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


def acc_data_read():
    # --- Read Acc Data --- #
    accData = [0, 0, 0, 0, 0, 0]
    value = [0.0, 0.0, 0.0]
    for i in range(6):
        try:
            accData[i] = i2c.read_byte_data(
                ACC_ADDRESS, ACC_REGISTER_ADDRESS + i)
        except:
            pass

    for i in range(3):
        value[i] = (accData[2 * i + 1] * 16) + (int(accData[2 * i] & 0xF0) / 16)
        value[i] = value[i] if value[i] < 2048 else value[i] - 4096
        value[i] = value[i] * 0.0098 * 1

    return value


print('----i2cdetect----')
os.system('i2cdetect -y 1')

print('\n----camera----')
os.system('vcgencmd get_camera')
try:
    take.picture(camerapath)
except:
    print('error : camera\n')

print('\n---Environment---')
try:
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    for _ in range(5):
        bme_data = bme280.bme280_read()
        print(bme_data)
        time.sleep(1)
except:
    print('error : env')

print('---melt----')
try:
	melt.down()
except:
	pi.write(meltPin, 0)


print('---motor---')
motor.setup()
motor.move(20, 20, 2)

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
        acc_data = acc_data_read()
        print(acc_data)
        time.sleep(0.2)
except:
    print('error : acc')

print('---xbee---')
try:
    xbee.on()
    for i in range(10):
        xbee.str_trans(str(i) + '  : reseive?')
except:
    print('error : xbee')

print('---gps---')
try:
    gps.open_gps()
    data = gps.gps_data_read()
    print(data)
except:
    print('error : gps')
