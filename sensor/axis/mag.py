from smbus import SMBus
import time
import datetime

from . import bmc050

MAG_ADDRESS = 0x13
MAG_REGISTER_ADDRESS = 0x42

i2c = SMBus(1)

def bmc050_setup():
    """
    6軸センサのセットアップをするための関数
    """
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

def mag_read():
    """
    磁気を読み取るための関数
    """
    # --- Read Mag Data --- #
    
    magData = [0, 0, 0, 0, 0, 0, 0, 0]
    value = [0.0, 0.0, 0.0]
    for i in range(8):
        
        magData[i] = i2c.read_byte_data(
            MAG_ADDRESS, MAG_REGISTER_ADDRESS + i)
        
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
        bmc050.bmc050_error()
    else:
        pass
    return value

# def mag_read():
#     """
#     磁気を読み取るための関数
#     """
#     # --- Read Mag Data --- #
#     while 1:
#         magData = [0, 0, 0, 0, 0, 0, 0, 0]
#         value = [0.0, 0.0, 0.0]
#         for i in range(8):
#             try:
#                 magData[i] = i2c.read_byte_data(
#                     MAG_ADDRESS, MAG_REGISTER_ADDRESS + i)
#             except:
#                 pass
#                 # print("error")

#         for i in range(3):
#             if i != 2:
#                 value[i] = ((magData[2*i+1] * 256) + (magData[2*i] & 0xF8)) / 8
#                 if value[i] > 4095:
#                     value[i] = value[i] - 8192
#             else:
#                 value[i] = ((magData[2*i+1] * 256) | (magData[2*i] & 0xF8)) / 2
#                 if value[i] > 16383:
#                     value[i] = value[i] - 32768
#         if value == [0.0, 0.0, 0.0] :
#             bmc050.bmc050_error()
#         else:
#             break
#     return value

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
            magData = mag_read()
            print(magData)
            time.sleep(1)

    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e.message)
