import datetime
import time

from sensor.gps import gps_navigate
from sensor.gps import gps
from sensor.axis import acc, mag, bmc050
import motor
from sensor.communication import xbee
import calibration
import stuck
import other


def angle_goal(magx_off, magy_off, lon2, lat2):
    """
    ゴールとの相対角度を算出する関数

    -180~180度
    """
    magdata = bmc050.mag_read()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    direction = calibration.calculate_direction(lon2, lat2)
    azimuth = direction["azimuth1"]
    angle_relative = azimuth - theta
    if angle_relative >= 0:
        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
    else:
        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
    return angle_relative


def adjust_direction(theta, magx_off, magy_off, lon2, lat2):
    """
    方向調整
    """
    an = input("出力どうする")
    while 1:
        print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')
        stuck.ue_jug()

        if 45 < theta <= 180:
            motor.motor_continue(an, -an)
        elif -180 < theta < -45:
            motor.motor_continue(-an, an)
        elif 0 <= theta <= 45:
            motor.deceleration(an, -an)
            break
        elif -45 <= theta <= 0:
            motor.motor_continue(-an, an)
            break

        theta = angle_goal(magx_off, magy_off, lon2, lat2)
        print('Calculated angle_relative: {theta}')
        time.sleep(0.03)


if __name__ == "__main__":
    lon2, lat2 = 139.908898, 35.918548
    lat2 = 35.9212680
    lon2 = 139.9109584
    stuck.ue_jug()

    # ------------- calibration -------------#
    # xbee.str_trans('calibration Start')
    print('##--calibration Start--##\n')
    magx_off, magy_off = calibration.cal(40, -40, 30)
    print(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')

    theta = angle_goal(magx_off, magy_off, lon2, lat2)
    adjust_direction(magx_off, magy_off, lon2, lat2)
