from smbus import SMBus
import time
import datetime

import other

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
        return True
    except:
        time.sleep(0.1)
        print("BMC050 Setup Error")
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)
        return False

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


if __name__ == '__main__':
    try:
        bmc050_setup()
        time.sleep(0.2)
        startTime = time.time()
        while 1:
            accData = acc_dataRead()
            norm = (accData[0]^2 + accData[1]^2 + accData[2]^2) ** 0.5
            print(f'x:{accData[0]}\ty:{accData[1]}\tz:{accData[2]}\tnorm:{norm}')
            other.saveLog('BMC050test', datetime.datetime.now(), startTime - time.time(), accData[0], accData[1], accData[2])
            time.sleep(1)

    except KeyboardInterrupt:
        print()
    except Exception as e:
        print('fuck')
        #print(e.message)
