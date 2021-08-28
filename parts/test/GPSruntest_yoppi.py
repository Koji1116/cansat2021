import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
import BMC050
import GPS
import motor
from parts import calibration
import time
import mag

# --- original module ---#

# --- must be installed module ---#
# import numpy as np

# --- default module ---#
# import difflib

GPS_data = [0.0, 0.0, 0.0, 0.0, 0.0]


def timer(t):
    global cond
    time.sleep(t)
    cond = False


def adjust_direction(theta):
    global magx_off
    global magy_off
    """
    方向調整
    """
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    count = 0
    t_small = 0.1
    t_big = 0.2
    while 15 < theta < 345:

        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1')
            motor.move(20, -20, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2')
            motor.move(20, -20, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3')
            motor.move(-20, 20, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4')
            motor.move(-20, 20, t_big)

        # count += 1
        data = calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = calibration.angle(magx, magy, magx_off, magy_off)
        direction = calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth - theta
        if theta < 0:
            theta = 360 + theta
        elif 360 <= theta <= 450:
            theta = theta - 360
        print('計算後のゴールとなす角度theta' + str(theta))

    print('theta = ' + str(theta) + '---回転終了!!!')


if __name__ == "__main__":
    motor.setup()
    mag.bmc050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.9105443
    lat2 = 35.9233106

    # ------------- program start -------------#
    direction = calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    aaa = direction['azimuth1']
    print('goal distance = ' + str(goal_distance))
    print('goal direction = ' + str(aaa))
    count = 0
    ##-----------テスト用--------
    r = float(input('右の出力は？'))
    l = float(input('左の出力は？'))
    t = float(input('何秒回転する？'))
    n = int(input('データ数いくつ'))
    while goal_distance >= 10:
        if count % 4 == 0:
            # ------------- calibration -------------#
            print('calibration Start')
            mag.bmc050_setup()
            magdata_Old = calibration.magdata_matrix(l, r, t, n)
            _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(magdata_Old)
        print('gps run strat')
        # ------------- gps navigate -------------#
        magdata = BMC050.mag_dataread()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
        direction = calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth - theta
        if theta < 0:
            theta = 360 + theta
        elif 360 <= theta <= 450:
            theta = theta - 360

        adjust_direction(theta)
        print('theta = ' + str(theta) + '---直進開始')
        ######直進するように左の出力強くしてます↓ 7/28 by oosima
        motor.move(65, 50, 6)

        # --- calculate  goal direction ---#
        direction = calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print('------ゴールとの距離は' + str(goal_distance) + 'm------')
        count += 1
