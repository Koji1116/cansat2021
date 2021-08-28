<<<<<<< HEAD:sensor/axis/mag.py
=======
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
from smbus import SMBus
import time
import BMC050
>>>>>>> 750264f8679bb62d140db0d7faa7e1643937f205:SensorModule/6-axis/mag.py
import datetime

from parts.other import other

MAG_ADDRESS = 0x13
MAG_REGISTER_ADDRESS = 0x42

i2c = SMBus(1)

def bmc050_setup():
    # --- BMC050Setup --- #

    # Initialize MAG
    try:
        data = i2c.read_byte_data(MAG_ADDRESS, 0x4B)
        if(data == 0):
            i2c.write_byte_data(MAG_ADDRESS, 0x4B, 0x83)
            time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4B, 0x01)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4C, 0x38)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4E, 0x84)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x51, 0x04)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x52, 0x0F)
        time.sleep(0.1)
    except:
        time.sleep(0.1)
        print("BMC050 Setup Error")
        data = i2c.read_byte_data(MAG_ADDRESS, 0x4B)
        if(data == 0):
            i2c.write_byte_data(MAG_ADDRESS, 0x4B, 0x83)
            time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4B, 0x01)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4C, 0x38)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x4E, 0x84)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x51, 0x04)
        time.sleep(0.1)
        i2c.write_byte_data(MAG_ADDRESS, 0x52, 0x0F)
        time.sleep(0.1)

def mag_dataRead():
    # --- Read Mag Data --- #
    while 1:
        magData = [0, 0, 0, 0, 0, 0, 0, 0]
        value = [0.0, 0.0, 0.0]
        for i in range(8):
            try:
                magData[i] = i2c.read_byte_data(
                    MAG_ADDRESS, MAG_REGISTER_ADDRESS + i)
            except:
                pass
                # print("error")

        for i in range(3):
            if i != 2:
                value[i] = ((magData[2*i+1] * 256) + (magData[2*i] & 0xF8)) / 8
                if value[i] > 4095:
                    value[i] = value[i] - 8192
            else:
                value[i] = ((magData[2*i+1] * 256) | (magData[2*i] & 0xF8)) / 2
                if value[i] > 16383:
                    value[i] = value[i] - 32768
        if value == [0.0, 0.0, 0.0] :
            BMC050.BMC050_error()
        else:
            break
    return value



if __name__ == '__main__':
    try:
        bmc050_setup()
        time.sleep(0.2)
        startTime = time.time()
        while 1:
            magData = mag_dataRead()
            print(magData)
            other.saveLog('BMC050_mag_test', datetime.datetime.now(), time.time() - startTime, magData[0], magData[1], magData[2])
            time.sleep(1)

    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e.message)
