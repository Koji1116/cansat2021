import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
from time import sleep
import acc
import time


if __name__ == '__main__':
    acc.bmc050_setup()

    s = input('a だったら確認テスト')
    
    while 1:
        if s =='a':
            accdata = acc.acc_dataread()
            z = accdata[2]
            if z <8:
                print('逆になってる')
            else:
                print('通常')
        else:
            accdata = acc.acc_dataread()
            # x = accdata[0]
            # y = accdata[1]
            z = accdata[2]
            print(z)
        time.sleep(1)
