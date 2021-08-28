# 着地判定後にキャリブレーション前にパラシュート回避を行う
# パラシュート回避エリアは設定せずに、パラシュートが検出されない場合が3回以上(下のプログラムのzで設定)
# のときパラシュート回避を行ったと判定
# そこでキャリブレーションを行い、ローバーをゴール方向に向かせる。
# そのあとにもう一度パラシュート回避を同じ判定方法で行ってGPS走行に移行する。

import time
import traceback

from parts.detection import paradetection
from parts.sensor.motor import motor
from parts.sensor.gps import gps
from parts.sensor.gps import gps_navigate


def land_point_save():
    try:
        while True:
            value = gps.readGPS()
            latitude_land = value[1]
            longitude_land = value[2]
            time.sleep(1)
            if latitude_land != -1.0 and longitude_land != 0.0:
                break
    except KeyboardInterrupt:
        gps.closeGPS()
        print("\r\nKeyboard Intruppted, Serial Closed")
    except:
        gps.closeGPS()
        print(traceback.format_exc())
    return longitude_land, latitude_land


def Parachute_area_judge(longitude_land, latitude_land):
    try:
        while True:
            value = gps.readGPS()
            latitude_new = value[1]
            longitude_new = value[2]
            print(value)
            print('longitude = ' + str(longitude_new))
            print('latitude = ' + str(latitude_new))
            time.sleep(1)
            if latitude_new != -1.0 and longitude_new != 0.0:
                break
    except KeyboardInterrupt:
        gps.closeGPS()
        print("\r\nKeyboard Intruppted, Serial Closed")

    except:
        gps.closeGPS()
        print(traceback.format_exc())
    direction = gps_navigate.vincenty_inverse(longitude_land, latitude_land, longitude_new, latitude_new)
    distance = direction["distance"]
    return distance


def Parachute_Avoidance(flug, goalGAP):
    # --- There is Parachute around rover ---#

    if flug == 1:
        # --- Avoid parachute by back control ---#
        try:
            # goalflug, goalarea, goalGAP, photoname = photorunning.GoalDetection("photostorage/photostorage_paradete/para",320,240,200,10,120)
            if goalGAP >= -100 and goalGAP <= -50:
                motor.move(50, -50, 0.1)
                # motor.move(50, 50, 1)
                # print('# motor.move(50, -50, 0.1)# motor.move(70, 70, 1)')
            if goalGAP >= -50 and goalGAP <= 0:
                motor.move(50, -50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(80, -80, 1)motor.move(70, 70, 1)')
            if goalGAP >= 0 and goalGAP <= 50:
                motor.move(-50, 50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(-50, 50, 0.1)motor.move(70, 70, 1)')
            if goalGAP >= 50 and goalGAP <= 100:
                motor.move(-50, 50, 0.1)
                # motor.move(50, 50, 1)
                # print(' # motor.move(-80, 80, 1)# motor.move(70, 70, 1)')

        except KeyboardInterrupt:
            print("stop")
    if flug == -1 or flug == 0:
        # print('flug')
        motor.move(50, 50, 0.5)


if __name__ == '__main__':
    try:
        motor.setup()
        # print("START: Judge covered by Parachute")
        # TSL2561.tsl2561_setup()
        # t2 = time.time()
        # t1 = t2
        # --- Paracute judge ---#
        # --- timeout is 60s ---#
        # while t2 - t1 < 60:
        # Luxflug = ParaDetection.ParaJudge(10000)
        # print(Luxflug)
        # if Luxflug[0] == 1:
        #	break
        # t1 =time.time()
        # time.sleep(1)
        # print("rover is covered with parachute!")

        print("START: Parachute avoidance")

        flug, area, gap, photoname = paradetection.paradetection("photostorage/photostorage_paradete/para", 320, 240,
                                                                 200, 10, 120, 1)
        print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
        print("paradetection phase success")
        count_paraavo = 0
        while count_paraavo < 3:
            flug, area, gap, photoname = paradetection.paradetection("photostorage/photostorage_paradete/para", 320,
                                                                     240, 200, 10, 120, 1)
            print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
            Parachute_Avoidance(flug, gap)
            print(flug)
            if flug == -1 or flug == 0:
                count_paraavo += 1
                print(count_paraavo)

        print("パラシュート回避完了")

    except KeyboardInterrupt:
        print("emergency!")

    except:
        print(traceback.format_exc())
    print("finish!")
