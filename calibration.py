# --- must be installed module ---#import numpy as np
import math
import time
import traceback
import datetime
import numpy as np

from sensor.axis import mag
from sensor.axis.bmc050 import bmc050_setup
from sensor.gps import gps
from sensor.gps import gps_navigate
from other import print_xbee
import motor
import stuck
import other

path_log = '/home/pi/Desktop/cansat2021/log/calibration.txt'


# filecount = len(glob.glob1(path_log, '*' + '.txt'))

# Calibration_rotate_controlLog = '/home/pi/log/Calibration_rotate_controlLog.txt'


def get_data():
    """
        MBC050からデータを得る
        """
    try:
        magData = mag.mag_read()
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print()
        print(e)
    # --- get magnet sensor data ---#
    magx = magData[0]
    magy = magData[1]
    magz = magData[2]
    return magx, magy, magz


def get_data_offset(magx_off, magy_off, magz_off):
    """
        MBC050からオフセットを考慮して磁気データを得る関数
        """
    try:
        magData = mag.mag_read()
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print()
        print(e)
    # --- get magnet sensor data ---#
    magx = magData[0] - magx_off
    magy = magData[1] - magy_off
    magz = magData[2] - magz_off
    return magx, magy, magz


def magdata_matrix(l, r, n):
    """
        キャリブレーション用の地磁気データを得るための関数。
        モータを連続的に動かして回転して地磁気データを得る。
        """
    try:
        stuck.ue_jug()
        magx, magy, magz = get_data()
        magdata = np.array([[magx, magy, magz]])
        for _ in range(n - 1):
            motor.motor_continue(l, r)
            magx, magy, magz = get_data()
            print(magx, magy)
            # --- multi dimention matrix ---#
            magdata = np.append(magdata, np.array(
                [[magx, magy, magz]]), axis=0)
            time.sleep(0.03)
        motor.deceleration(l, r)
    except KeyboardInterrupt:
        print('Interrupt')
    except Exception as e:
        print(e.message())
    return magdata


def magdata_matrix_hand():
    """
        キャリブレーション用の磁気値を手持ちで得るための関数
        """
    try:
        magx, magy, magz = get_data()
        magdata = np.array([[magx, magy, magz]])
        for i in range(60):
            print('少し回転')
            time.sleep(1)
            print(f'{i + 1}回目')
            magx, magy, magz = get_data()
            # --- multi dimention matrix ---#
            magdata = np.append(magdata, np.array(
                [[magx, magy, magz]]), axis=0)
    except KeyboardInterrupt:
        print('Interrupt')
    except Exception as e:
        print(e.message())
    return magdata


def magdata_matrix_offset(l, r, t, magx_off, magy_off, magz_off):
    """
        オフセットを考慮したデータセットを取得するための関数
        """
    try:
        magx, magy, magz = get_data_offset(magx_off, magy_off, magz_off)
        magdata = np.array([[magx, magy, magz]])
        for _ in range(20):
            motor(l, r, t)
            magx, magy, magz = get_data_offset(magx_off, magy_off, magz_off)
            # --- multi dimention matrix ---#
            magdata = np.append(magdata, np.array(
                [[magx, magy, magz]]), axis=0)
    except KeyboardInterrupt:
        print_xbee('Interrupt')
    except Exception as e:
        print_xbee(e.message())
    return magdata


def calculate_offset(magdata):
    """
    オフセットを計算する関数
    """
    # --- manage each element sepalately ---#
    magx_array = magdata[:, 0]
    magy_array = magdata[:, 1]
    magz_array = magdata[:, 2]

    # --- find maximam gps value and minimam gps value respectively ---#
    magx_max = magx_array[np.argmax(magx_array)]
    magy_max = magy_array[np.argmax(magy_array)]
    magz_max = magz_array[np.argmax(magz_array)]

    magx_min = magx_array[np.argmin(magx_array)]
    magy_min = magy_array[np.argmin(magy_array)]
    magz_min = magz_array[np.argmin(magz_array)]

    # --- calucurate offset ---#
    magx_off = (magx_max + magx_min) / 2
    magy_off = (magy_max + magy_min) / 2
    magz_off = (magz_max + magz_min) / 2

    # --- save offset --- #
    other.log('/home/pi/Desktop/cansat2021/log/calibrationLog.txt',
              datetime.datetime.now(), magx_off, magy_off)

    return magx_array, magy_array, magz_array, magx_off, magy_off, magz_off


def cal(l, r, n):
    magdata = magdata_matrix(l, r, n)
    _, _, _, magx_off, magy_off, _ = calculate_offset(magdata)
    return magx_off, magy_off


def angle(magx, magy, magx_off=0, magy_off=0):
    if magy - magy_off == 0:
        magy += 0.000001
    θ = math.degrees(math.atan((magy - magy_off) / (magx - magx_off)))

    if magx - magx_off > 0 and magy - magy_off > 0:  # First quadrant
        pass  # 0 <= θ <= 90
    elif magx - magx_off < 0 and magy - magy_off > 0:  # Second quadrant
        θ = 180 + θ  # 90 <= θ <= 180
    elif magx - magx_off < 0 and magy - magy_off < 0:  # Third quadrant
        θ = θ + 180  # 180 <= θ <= 270
    elif magx - magx_off > 0 and magy - magy_off < 0:  # Fourth quadrant
        θ = 360 + θ  # 270 <= θ <= 360

    θ += 90
    if 360 <= θ <= 450:
        θ -= 360
    return θ


def calculate_direction(lon2, lat2):
    # --- read gps data ---#
    try:
        gps.open_gps()
        utc, lat, lon, sHeight, gHeight = gps.gps_data_read()
        lat1 = lat
        lon1 = lon
    except KeyboardInterrupt:
        gps.close_gps()
        print_xbee("\r\nKeyboard Intruppted, Serial Closed")
    except:
        gps.close_gps()
        print_xbee(traceback.format_exc())
    # --- calculate angle to goal ---#
    direction = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    return direction


if __name__ == "__main__":
    motor.setup()
    bmc050_setup()
    magdata =magdata_matrix(80, -80, 1000)


    # try:
    #     r = float(input('右の出力は？'))
    #     l = float(input('左の出力は？'))
    #     t = float(input('一回の回転時間は？'))
    #     # n = int(input("取得するデータ数は？"))
    #     # --- setup ---#
    #     mag.bmc050_setup()
    #     t_start = time.time()
    #     # --- calibration ---#
    #     magdata_Old = magdata_matrix(l, r, t)
    #     # --- calculate offset ---#
    #     magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = calculate_offset(
    #         magdata_Old)
    #     time.sleep(0.1)
    #     # ----Take magnetic data considering offset----#
    #     magdata_new = magdata_matrix_offset(
    #         l, r, t, magx_off, magy_off, magz_off)
    #     magx_array_new = magdata_new[:, 0]
    #     magy_array_new = magdata_new[:, 1]
    #     magz_array_new = magdata_new[:, 2]
    #     for i in range(len(magx_array_new)):
    #         other.log(
    #             path_log, magx_array_Old[i], magy_array_Old[i], magx_array_new[i], magy_array_new[i])
    #     print_xbee("success")

    # except KeyboardInterrupt:
    #     print_xbee("Interrupted")

    # finally:
    #     print_xbee("End")

