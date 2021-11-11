import time
import cv2
import sys
import numpy as np

from sensor.camera import take
from sensor.communication import xbee
from sensor.axis import mag, bmc050
from other import print_xbee
import motor
import stuck
import calibration
import other
import gpsrunning

# 写真内の赤色面積で進時間を決める用　調整必要
area_short = 59.9
area_middle = 6
area_long = 1


def get_center(contour):
    """
    輪郭の中心を取得する。
    """
    # 輪郭のモーメントを計算する。
    M = cv2.moments(contour)
    # モーメントから重心を計算する。
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        # set values as what you need in the situation
        cx, cy = 0, 0

    return cx, cy


def mosaic(src, ratio):
    small = cv2.resize(src, None, fx=ratio, fy=ratio,
                       interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)


# def detect_red():
#     img_original = cv2.imread('元画像のパス')
#     img_mosaic = mosaic(img_original, ratio=0.3)
#     img_hsv = cv2.cvtColor(img_mosaic, cv2.COLOR_BGR2HSV)
#
#     red_min = np.array([120, 120, 100], np.uint8)
#     red_max = np.array([255, 255, 255], np.uint8)
#     red_img = cv2.inRange(img_hsv, red_min, red_max)
#     red_img_gry = cv2.cvtColor(red_img, cv2.COLOR_GRAY2RGB)
#
#     cv2.imwrite(path_detection, red_img_gry)


def goal_detection(imgpath: str, G_thd: float):
    try:
        img = cv2.imread(imgpath)
        hig, wid, _ = img.shape
        img_mosaic = mosaic(img, ratio=0.3)
        img_hsv = cv2.cvtColor(img_mosaic, cv2.COLOR_BGR2HSV)

        # 最小外接円を描いた写真の保存先
        path_detection = other.filename(
            '/home/pi/Desktop/Cansat2021ver/detected/Detected-', 'jpg')

        red_min = np.array([120, 120, 120], np.uint8)
        red_max = np.array([255, 255, 255], np.uint8)
        mask = cv2.inRange(img_hsv, red_min, red_max)
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_area_contour = -1

        if len(contours) > 0:
            radius_frame = ()
            for (i, cnt) in zip(range(0, len(contours)), contours):
                print_xbee(f'i:{i}')
                # 赤色検知した部分に最小外接円を書く
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                radius_frame = cv2.circle(img, center, radius, (0, 0, 255), 2)
                print_xbee(radius_frame)
                # 検知した赤色の面積の中で最大のものを探す
                area = cv2.contourArea(contours[i])
                if max_area < area:
                    max_area = area
                    max_area_contour = i
            cv2.imwrite(path_detection, radius_frame)
        else:
            cv2.imwrite(path_detection, img)

        max_area /= hig * wid
        max_area *= 100

        centers = get_center(contours[max_area_contour])

        if max_area_contour == -1:
            return (-1, 0, 1000, imgpath, path_detection)
        elif max_area <= 0.1:
            return (-1, max_area, 1000000, imgpath, path_detection)
        elif max_area >= G_thd:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return (1, max_area, GAP, imgpath, path_detection)
        else:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return (0, max_area, GAP, imgpath, path_detection)
    except:
        return (1000, 1000, 1000, imgpath, path_detection)


def adjustment_mag(strength, t, magx_off, magy_off):
    print("1")
    
    magdata = mag.mag_read()
    mag_x_old = magdata[0]
    mag_y_old = magdata[1]
    theta_old = calibration.angle(mag_x_old, mag_y_old, magx_off, magy_off)
    t_start = time.time()  
    while time.time() - t_start <= t:
        print("4")
        strength_adj = strength
        magdata = mag.mag_read()
        mag_x = magdata[0]
        mag_y = magdata[1]

        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
        angle_relative = theta_old - theta
        if angle_relative >= 0:
            angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
        else:
            angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
        if angle_relative >= 0:
            if angle_relative <= 15:
                adj = 0
            elif angle_relative <= 90:
                adj = strength_adj * 0.25
            else:
                adj = strength_adj * 0.4
        else:
            if angle_relative >= -15:
                adj = 0
            elif angle_relative >= -90:
                adj = strength * -0.25
            else:
                adj = strength_adj * -0.4
        print_xbee(f'angle ----- {angle_relative}')
        print("3#)")
        strength_l, strength_r = strength_adj + adj, strength_adj - adj + 5
        print_xbee(f'motor power:\t{strength_l}\t{strength_r}')
        motor.motor_continue(strength_l, strength_r)
        time.sleep(0.1)
        mag_x_old = mag_x
        mag_y_old = mag_y
        theta_old = calibration.angle(mag_x_old, mag_y_old, magx_off, magy_off)
    print("123")
    strength_l, strength_r = 20, 20
    motor.deceleration(strength_l, strength_r)


def image_guided_driving(log_photorunning, G_thd, magx_off, magy_off, lon2, lat2, thd_distance, t_adj_gps, gpsrun=False):
    try:
        t_start = time.time()
        count_short_l = 0
        count_short_r = 0
        adj_short = 0
        auto_count = 0
        while 1:
            stuck.ue_jug()
            path_photo = '/home/pi/Desktop/Cansat2021ver/photo_imageguide/ImageGuide-'
            photoName = take.picture(path_photo)
            goalflug, goalarea, gap, imgname, imgname2 = goal_detection(
                photoName, 50)
            print_xbee(
                f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}\timagename:{imgname}\timagename2:{imgname2}')
            other.log(log_photorunning, t_start - time.time(),
                      goalflug, goalarea, gap, imgname, imgname2)
            if auto_count >= 8 and goalarea >= 0.005 and goalarea != 1000 and goalflug == -1:

                ##赤色が見つからなかった時用に##
                print_xbee("small red found run")
                print(goalarea)
                adjustment_mag(40, 1.5, magx_off, magy_off)
                auto_count = 0

            if goalflug == -1 or goalflug == 1000:
                print_xbee('Nogoal detected')
                motor.move(40, -40, 0.1)
                auto_count += 1
            elif goalarea <= area_long:
                auto_count = 0
                if -100 <= gap and gap <= -65:
                    print_xbee('Turn left')
                    motor.move(-33, 33, 0.1)
                elif 65 <= gap and gap <= 100:
                    print_xbee('Turn right')
                    motor.move(33, -33, 0.1)
                else:
                    print_xbee('Go straight long')
                    adjustment_mag(40, 1.4, magx_off, magy_off)
            elif goalarea <= area_middle:
                auto_count = 0
                if -100 <= gap and gap <= -65:
                    print_xbee('Turn left')
                    motor.move(-25, 25, 0.1)
                elif 65 <= gap and gap <= 100:
                    print_xbee('Turn right')
                    motor.move(25, -25, 0.1)
                else:
                    print_xbee('Go straight middle')
                    adjustment_mag(40, 0.8, magx_off, magy_off)
            elif goalarea <= area_short:
                auto_count = 0
                if -100 <= gap and gap <= -65:
                    print_xbee('Turn left')
                    count_short_l += 1
                    adj_short = 0
                    if count_short_r % 4 == 0:
                        adj_short += 3
                        print_xbee('#-Power up-#')
                    motor.move(-20 - adj_short, 20 + adj_short, 0.1)
                elif 65 <= gap and gap <= 100:
                    print_xbee('Turn right')
                    count_short_r += 1
                    if count_short_r % 4 == 0:
                        adj_short += 3
                        print_xbee('#-Power up-#')
                    motor.move(20 + adj_short, -20 - adj_short, 0.1)
                else:
                    print_xbee('Go stright short')
                    adjustment_mag(40, 0.6, magx_off, magy_off)
                    count_short_l = 0
                    count_short_r = 0
                    adj_short = 0
            elif goalarea >= G_thd:
                print_xbee('###---Goal---###')
                print_xbee('###---Goal---###')
                break

            # ゴールから離れた場合GPS誘導に移行
            if gpsrun:
                direction = calibration.calculate_direction(lon2, lat2)
                goal_distance = direction['distance']
                if goal_distance >= thd_distance + 2:
                    gpsrunning.drive(lon2, lat2, thd_distance, t_adj_gps,
                                     logpath='/home/pi/Desktop/Cansat2021ver/log/gpsrunning(image)Log', t_start=0)
    except KeyboardInterrupt:
        print_xbee('stop')
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))


if __name__ == "__main__":
    try:
        bmc050.bmc050_error()
        # Initialize
        lat2 = 35.9236093
        lon2 = 139.9118821
        G_thd = 60
        log_photorunning = '/home/pi/Desktop/Cansat2021ver/log/photorunning_practice.txt'
        motor.setup()

        # calibration
        print_xbee('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, -40, 30)
        print_xbee(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        print_xbee('##--calibration end--##')

        # Image Guide
        image_guided_driving(log_photorunning, G_thd, magx_off,
                             magy_off, lon2, lat2, thd_distance=5, t_adj_gps=60)

    except KeyboardInterrupt:
        print_xbee('stop')
        xbee.off()
    except Exception as e:
        xbee.off()
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
