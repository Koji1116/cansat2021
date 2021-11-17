import time
import datetime
import random
from other import print_xbee

from sensor.communication import xbee
import motor
from sensor.gps import gps_navigate
from sensor.gps import gps
from sensor.axis import bmc050
import other


def ue_jug():
    ue_count = 0
    """
    ローバーの状態を確認する関数
    通常状態：True
    逆さになってる：False
    加速度センサZ軸の正負で判定するよ
    """
    while 1:
        za = []
        for i in range(3):
            accdata = bmc050.acc_read()
            za.append(accdata[2])
            time.sleep(0.2)
        z = max(za)

        if z >= 7.5:
            xbee.str_trans('Upward')
            print('上だよ')
            break
        else:
            xbee.str_trans('Upside-down')
            print(f'下だよ{ue_count}')
            print(f'acc: {z}')
            if ue_count > 2:
                motor.move(30, 30, 0.008, False)
            elif ue_count > 8:
                motor.move(70, 70, 0.008, False)
            else:
                motor.move(12, 12, 0.2, False)
            time.sleep(2)
            ue_count += 1


def stuck_jug(lat1, lon1, lat2, lon2, thd=1.0):
    data_stuck = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    logpath_stuck = other.filename(
        '/home/pi/Desktop/cansat2021ver/log/stuck', 'txt')
    if data_stuck['distance'] <= thd:
        print_xbee(str(data_stuck['distance']) + '----!!!    stuck   !!!')
        other.log(logpath_stuck, datetime.datetime.now(),  lat2, lon2, 1)
        return False
    else:
        print_xbee(str(data_stuck['distance']) + '-----not stucked')
        other.log(logpath_stuck, datetime.datetime.now(),  lat2, lon2, 0)
        return True


def random(a, b, k):
    ns = []
    while len(ns) < k:
        n = random.randint(a, b)
        if not n in ns:
            ns.append(n)
    return ns


def stuck_avoid_move(x):
    if x == 0:
        print_xbee('sutck_avoid_move():0')
        motor.move(-100, -100, 5)
        motor.move(-60, -60, 3)
    elif x == 1:
        print_xbee('sutck_avoid_move():1')
        motor.move(40, -40, 1)
        motor.move(100, 100, 5)
    elif x == 2:
        print_xbee('sutck_avoid_move():2')
        motor.move(-100, 100, 2)
        motor.move(100, 100, 5)

    elif x == 3:
        print_xbee('sutck_avoid_move():3')
        motor.move(100, -100, 2)
        motor.move(100, 100, 5)

    elif x == 4:
        print_xbee('sutck_avoid_move():4')
        motor.move(40, -40, 1)
        motor.move(-80, -100, 5)

    elif x == 5:
        print_xbee('sutck_avoid_move():5')
        motor.move(40, -40, 1)
        motor.move(-100, -80, 5)

    elif x == 6:
        print_xbee('sutck_avoid_move():6')
        motor.move(100, -100, 3)
        motor.move(100, 100, 3)


def stuck_avoid():
    print_xbee('start stuck  avoid')
    flag = False
    while 1:
        lat_old, lon_old = gps.location()
        # 0~6
        for i in range(7):
            stuck_avoid_move(i)
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == True:
                flag = True
                break
        if flag:
            break
        # 3,2,1,0
        for i in range(7):
            stuck_avoid_move(7 - i)
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == False:
                # if i == 1 or i == 4 or i == 5:
                #     print('スタックもう一度引っかからないように避ける')
                #     motor.move(-60, -60, 2)
                #     motor.move(-60, 60, 0.5)
                #     motor.move(80, 80, 3)
                flag = True
                break
        if flag:
            break
        random = random(0, 6, 7)
        for i in range(7):
            stuck_avoid_move(random[i])
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == False:
                # if i == 1 or i == 4 or i == 5:
                #     print('スタックもう一度引っかからないように避ける')
                #     motor.move(-60, -60, 2)
                #     motor.move(-60, 60, 0.5)
                #     motor.move(80, 80, 3)
                flag = True
                break
        if flag:
            break
    print_xbee('complete stuck avoid')


if __name__ == '__main__':
    motor.setup()
    while 1:
        a = int(input('出力入力しろ'))
        b = float(input('時間入力しろ'))
        motor.move(a, a, b)
