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
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    stuck_count = 1
    t_small = 0.1
    t_big = 0.2
    force = 35
    while 30 < theta <= 180 or -180 < theta < -30:
        if stuck_count % 7 == 0:
            print('Increase output')
            force += 10
        if 30 <= theta <= 60:
            print(f'theta = {theta}\t---rotation_ver1 (stuck:{stuck_count})')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            print(f'theta = {theta}\t---rotation_ver2 (stuck:{stuck_count})')
            motor.move(force, -force, t_big)

        elif -60 <= theta <= -30:
            print(f'theta = {theta}\t---rotation_ver3 (stuck:{stuck_count})')
            motor.move(-force, force, t_small)
        elif -180 < theta < -60:
            print(f'theta = {theta}\t---rotation_ver4 (stuck:{stuck_count})')
            motor.move(-force, force, t_big)
        else:
            print(f'theta = {theta}')

        stuck_count += 1
        stuck.ue_jug()
        theta = angle_goal(magx_off, magy_off, lon2, lat2)
        print('Calculated angle_relative: {theta}')
        time.sleep(1)
    print(f'theta = {theta} \t rotation finished!!!')


def drive(lon2, lat2, thd_distance, t_adj_gps, logpath='/home/pi/Desktop/Cansat2021ver/log/gpsrunningLog', t_start=0):
    """
    GPS走行の関数
    統合する場合はprintをXbee.str_transに変更，other.saveLogのコメントアウトを外す
    """
    direction = calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    count_bmc050_erro = 0
    # anan = 0
    while goal_distance >= thd_distance:
        t_stuck_count = 1
        stuck.ue_jug()
        # if anan == 0:
        #     pass
        # else:
        #     # ------------- calibration -------------#
        #     # xbee.str_trans('calibration Start')
        #     print('##--calibration Start--##\n')
        #     magx_off, magy_off = calibration.cal(40, -40, 30)
        #     print(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        #     anan =1

        # ------------- calibration -------------#
        # xbee.str_trans('calibration Start')
        print('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, -40, 30)
        print(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')

        theta = angle_goal(magx_off, magy_off, lon2, lat2)
        adjust_direction(theta, magx_off, magy_off, lon2, lat2)

        t_cal = time.time()
        lat_old, lon_old = gps.location()
        mag_x_old, mag_y_old = 0, 0
        while time.time() - t_cal <= t_adj_gps:
            lat1, lon1 = gps.location()
            lat_new, lon_new = lat1, lon1
            direction = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
            azimuth, goal_distance = direction["azimuth1"], direction["distance"]
            print(
                f'lat: {lat1}\tlon: {lon1}\tdistance: {goal_distance}\tazimuth: {azimuth}\n')
            xbee.str_trans(
                f'lat: {lat1}\tlon: {lon1}\tdistance: {direction["distance"]}\ttheta: {theta}')
            other.log(logpath, datetime.datetime.now(), time.time() -
                      t_start, lat1, lon1, direction['distance'], azimuth)
            if t_stuck_count % 8 == 0:
                if stuck.stuck_jug(lat_old, lon_old, lat_new, lon_new, 2):
                    pass
                else:
                    stuck.stuck_avoid()
                    pass
                lat_old, lon_old = gps.location()

            if goal_distance <= thd_distance:
                break
            else:
                for _ in range(50):
                    #theta = angle_goal(magx_off, magy_off)
                    magdata = bmc050.mag_read()
                    mag_x = magdata[0]
                    mag_y = magdata[1]
                    if mag_x == mag_x_old and mag_y == mag_y_old:
                        count_bmc050_erro += 1
                        if count_bmc050_erro >= 3:
                            print('-------mag_x mag_y error-----修復開始')
                            bmc050.bmc050_error()
                            magdata = bmc050.mag_read()
                            mag_x = magdata[0]
                            mag_y = magdata[1]
                            count_bmc050_erro = 0
                    else:
                        count_bmc050_erro = 0
                    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
                    # if mag_x == mag_x_old and mag_y == mag_y_old:
                    #     count_bmc050_erro += 1
                    #     if count_bmc050_erro >= 3:
                    #         print('-------mag_x mag_y error-----switch start  ')
                    #         motor.motor_stop(0.5)
                    #         BMC050.BMC050_error()
                    #         stuck.ue_jug()
                    #         magdata = BMC050.mag_dataRead()
                    #         mag_x = magdata[0]
                    #         mag_y = magdata[1]
                    #         count_bmc050_erro = 0
                    # else:
                    #     count_bmc050_erro = 0
                    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
                    angle_relative = azimuth - theta
                    if angle_relative >= 0:
                        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
                    else:
                        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
                    theta = angle_relative
                    adj_r = 0
                    # if theta >= 0:
                    #     if theta <= 8:
                    #         adj = 0
                    #     elif theta <= 15:
                    #         adj = 5
                    #     elif theta <= 90:
                    #         adj = 20
                    #         adj_r = 5
                    #     else:
                    #         adj = 30
                    #         adj_r = 5
                    # else:
                    #     if theta >= - 8:
                    #         adj = 0
                    #     elif theta >= -15:
                    #         adj = -10
                    #     elif theta >= -90:
                    #         adj = -20
                    #     else:
                    #         adj = -30
                    if theta >= 0:
                        if theta <= 15:
                            adj = 0
                        elif theta <= 90:
                            adj = 20
                            adj_r = 5
                        else:
                            adj = 30
                            adj_r = 5
                    else:
                        if theta >= -15:
                            adj = 0
                        elif theta >= -90:
                            adj = -20
                        else:
                            adj = -30
                    print(f'angle ----- {theta}')
                    strength_l, strength_r = 70 + adj, 70 - adj - adj_r
                    motor.motor_continue(strength_l, strength_r)
                    time.sleep(0.02)
                    mag_x_old = mag_x
                    mag_y_old = mag_y
            t_stuck_count += 1
        motor.deceleration(strength_l, strength_r)
        time.sleep(2)
        lat_new, lon_new = gps.location()

        direction = calibration.calculate_direction(lon2, lat2)
        goal_distance = direction['distance']
        print(f'-----distance: {goal_distance}-----')


if __name__ == '__main__':
    # lat2 = 35.918548
    # lon2 = 139.908896
    lat2 = 35.9234892
    lon2 = 139.9118744
    gps.open_gps()
    bmc050.bmc050_setup()
    motor.setup()

    drive(lon2, lat2, thd_distance=10, t_adj_gps=60)
