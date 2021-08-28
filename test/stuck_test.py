#from sensor.gps.GPS_Navigate import vincenty_inverse
import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
from time import sleep
from math import*
from gpiozero import Motor
import BMC050
import Xbee
import stuck
import time
import motor
import GPS_Navigate
import GPS
import acc

def ue_jug():
    """
    ローバーの状態を確認する関数
    通常状態：True
    逆さになってる：False
    加速度センサZ軸の正負で判定するよ
    """
    acc.bmc050_setup()
    accdata = acc.acc_dataread()
    z = accdata[2]
    if z >= 0 :
        return True
    else:
        return False


def stuck_jug(lat1, lon1, lat2, lon2, thd =1 ):
    data_stuck =GPS_Navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    if data_stuck['distance'] >= thd:
        print('動いた距離 = '+str(data_stuck['distance']))
        print('not stuck')
        return True
    else:
        print('動いた距離 = '+str(data_stuck['distance']))
        print('fuck')
        return False


#def stuck_jud(thd=11):  # しきい値thd調整必要
    # BMC050.bmc050_setup()
    # acc_max = 0
    # for i in range(20):
    #     accdata = BMC050.acc_data()
    #     acc_x = accdata[0]
    #     acc_y = accdata[1]
    #     acc_z = accdata[2]
    #     acc = (acc_x**2 + acc_y**2 + acc_z**2)**0.5
    #     if acc_max < acc:
    #         acc_max = acc

    # if acc_max < thd:
    #     print('スタックした')
    #     Xbee.str_trans('スタックした')
    #     return True
    # else:
    #     print('まだしてない')
    #     Xbee.str_trans('まだしてない')
    #     return False


def stuck_avoid_move(x):
    if x == 0:
        print('sutck_avoid_move():0')
        motor.move(1, 1, 5)
        motor.move(1, 1, 3)
    elif x == 1:
        print('sutck_avoid_move():1')
        motor.move(-1, -1, 5)
        motor.move(-1, -1, 3)
    elif x == 2:
        print('sutck_avoid_move():2')
        motor.move(0.8, 1, 5)
        motor.move(1, 1, 3)

    elif x == 3:
        print('sutck_avoid_move():3')
        motor.move(1, 0.6, 5)
        motor.move(1, 1, 3)

    elif x == 4:
        print('sutck_avoid_move():4')
        motor.move(-0.6, -1, 5)
        motor.move(-1, -1, 3)

    elif x == 5:
        print('sutck_avoid_move():5')
        motor.move(-1, -0.6, 5)
        motor.move(-1, -1, 3)

    elif x == 6:
        print('sutck_avoid_move():6')
        motor.move(1, -1, 5)
        motor.move(1, 1, 3)



def stuck_avoid():
    motor.setup()
    print('スタック回避開始')
    flag = False
    while 1:
        # 0~6
        for i in range(7):
            utc1, lat1, lon1, sHeight1, gHeight1 = GPS.GPSdeta_read()
            stuck.stuck_avoid_move(i)
            utc2, lat2, lon2, sHeight2, gHeight2 = GPS.GPSdeta_read()
            bool_stuck = stuck.stuck_jud(lat1, lon1 ,lat2 , lon2,1)
            if bool_stuck == False:
                if i == 1 or i == 4 or i == 5:
                    print('スタックもう一度引っかからないように避ける')
                    motor.move(-0.8, -0.8, 2)
                    motor.move(0.2, 0.8, 1)
                    motor.move(0.8, 0.8, 3)
                flag = True
                break
        if flag:
            break
        # 3,2,1,0
        for i in range(7):
            utc1, lat1, lon1, sHeight1, gHeight1 = GPS.GPSdeta_read()
            stuck.stuck_avoid_move(7-i)
            utc2, lat2, lon2, sHeight2, gHeight2 = GPS.GPSdeta_read()
            bool_stuck = stuck.stuck_jud(lat1, lon1 ,lat2 , lon2,1)
            if bool_stuck == False:
                if i == 1 or i == 4 or i == 5:
                    print('スタックもう一度引っかからないように避ける')
                    motor.move(-0.8, -0.8, 2)
                    motor.move(0.2, 0.8, 1)
                    motor.move(0.8, 0.8, 5)
                flag = True
                break
        if flag:
            break
    print('スタック回避完了')


if __name__ == '__main__':
    GPS.openGPS()
    while 1:
        
        GPSdata_old = GPS.GPSdata_read()
        print('go')
        #motor.move(40, 40,  10)
        time.sleep(5)
        print('stop')
        GPSdata_new = GPS.GPSdata_read()
        if stuck_jug(GPSdata_old[1], GPSdata_old[2], GPSdata_new[1], GPSdata_new[2], 5):
            print('not stuck')
            
        else:
            print('fuck')
            

