# -*- coding: utf-8 -*-
import smbus
import time

ACCL_ADDR = 0x19
GYRO_ADDR = 0x69

bus = smbus.SMBus(1)

def bmc050_setup():


    # 加速度センサーの設定
    # Select PMU_Range register, 0x0F(15)
    #       0x03(03)    Range = +/- 2g
    bus.write_byte_data(ACCL_ADDR, 0x0F, 0x03)
    # Select PMU_BW register, 0x10(16)
    #       0x08(08)    Bandwidth = 7.81 Hz
    bus.write_byte_data(ACCL_ADDR, 0x10, 0x08)
    # Select PMU_LPW register, 0x11(17)
    #       0x00(00)    Normal mode, Sleep duration = 0.5ms
    bus.write_byte_data(ACCL_ADDR, 0x11, 0x00)

    time.sleep(0.5)




def accl():
    xA = yA = zA = 0

    try:
        data = bus.read_i2c_block_data(0x19, 0x02, 6)
        # Convert the data to 12-bits
        xA = ((data[1] * 256) + (data[0] & 0xF0)) / 16
        if xA > 2047:
            xA -= 4096
        yA = ((data[3] * 256) + (data[2] & 0xF0)) / 16
        if yA > 2047:
            yA -= 4096
        zA = ((data[5] * 256) + (data[4] & 0xF0)) / 16
        if zA > 2047:
            zA -= 4096
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

    return xA, yA, zA






if __name__ == "__main__":
    bmc050_setup()
    while True:
        xAccl, yAccl, zAccl = accl()

        print("acceleration -> x:{}, y:{}, z: {}".format(xAccl, yAccl, zAccl))
        time.sleep(0.1)