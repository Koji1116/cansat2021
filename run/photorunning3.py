import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')

import cv2
import numpy as np
import time
import Capture
# import stuck
import Xbee
import motor
import other
import datetime
import time
import mag
import calibration
import stuck
import BMC050

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


def GoalDetection(imgpath, H_min, H_max, S_thd, G_thd):
    try:
        imgname = imgpath
        img = cv2.imread(imgname)
        hig, wid, _ = img.shape

        img_HSV = cv2.cvtColor(cv2.GaussianBlur(img, (15, 15), 0), cv2.COLOR_BGR2HSV_FULL)
        h = img_HSV[:, :, 0]
        s = img_HSV[:, :, 1]
        mask = np.zeros(h.shape, dtype=np.uint8)
        mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_area_contour = -1

        for j in range(0, len(contours)):
            area = cv2.contourArea(contours[j])
            if max_area < area:
                max_area = area
                max_area_contour = j

        max_area /= hig * wid
        max_area *= 100

        centers = get_center(contours[max_area_contour])

        if max_area_contour == -1:
            return [-1, 0, 1000, imgname]
        elif max_area <= 0.2:
            return [-1, max_area, 1000000, imgname]
        elif max_area >= G_thd:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [1, max_area, GAP, imgname]
        else:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [0, max_area, GAP, imgname]
    except:
        return [1000, 1000, 1000, imgname]


def DrawContours(imgpath, H_min, H_max, S_thd):
    try:
        img = cv2.imread(imgpath)
        hig, wid, _ = img.shape

        img_HSV = cv2.cvtColor(cv2.GaussianBlur(img, (15, 15), 0), cv2.COLOR_BGR2HSV_FULL)
        h = img_HSV[:, :, 0]
        s = img_HSV[:, :, 1]
        mask = np.zeros(h.shape, dtype=np.uint8)
        mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            for cnt in contours:
                # 最小外接円を描く
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                radius_frame = cv2.circle(img, center, radius, (0, 0, 255), 2)

            path = other.fileName('photostorage/photorunning2-', 'jpg')
            cv2.imwrite(path, radius_frame)
                
            return path
        else:
            path = other.fileName('photostorage/photorunning2-', 'jpg')
            cv2.imwrite(path, img)
            return path
    except KeyboardInterrupt:
        print("end drawcircle")

def adjustment_mag(strength, t, magx_off, magy_off):
    count_bmc050_erro = 0
    t_start = time.time()
    magdata = mag.mag_dataread()
    mag_x_old = magdata[0]
    mag_y_old = magdata[1]
    theta_old = calibration.angle(mag_x_old, mag_y_old, magx_off, magy_off)
    while time.time()-t_start <= t:
        strength_adj = strength
        magdata = mag.mag_dataread()
        mag_x = magdata[0]
        mag_y = magdata[1]
        if mag_x == mag_x_old and mag_y == mag_y_old:
            count_bmc050_erro += 1
            if count_bmc050_erro >= 3:
                print('-------mag_x mag_y error-----修復開始')
                BMC050.bmc050_error()
                magdata = BMC050.mag_dataread()
                mag_x = magdata[0]
                mag_y = magdata[1]
                count_bmc050_erro = 0
        else:
            count_bmc050_erro = 0
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
        print(f'angle ----- {angle_relative}')
        strength_l, strength_r = strength_adj + adj, strength_adj - adj + 10
        motor.motor_continue(strength_l, strength_r)
        time.sleep(0.1)
        mag_x_old = mag_x
        mag_y_old = mag_y
        theta_old = calibration.angle(mag_x_old, mag_y_old, magx_off, magy_off)
    motor.deceleration(strength_l, strength_r)


def image_guided_driving(path_photo, log_photorunning, G_thd, magx_off, magy_off):
    try:
        t_start = time.time()
        while 1:
            stuck.ue_jug()
            photoName = Capture.Capture(path_photo)  # 解像度調整するところ？
            goalflug, goalarea, gap, imgname = GoalDetection(photoName, 200, 20, 80, 50)
            imgname2 = DrawContours(imgname, 200, 20, 80)
            print(f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}\timagename:{imgname}\timagename2:{imgname2}')
            other.saveLog(log_photorunning, t_start - time.time(), goalflug, goalarea, gap, imgname, imgname2)
            if goalflug == 1:
                break
            if goalflug == -1 or goalflug == 1000:
                print('Nogoal detected')
                motor.move(40, -40, 0.1)
            elif goalarea <= area_long:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    motor.move(-40, 40, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    motor.move(40, -40, 0.1)
                else:
                    print('Go straight long')
                    adjustment_mag(80, 3, magx_off, magy_off)
            elif goalarea <= area_middle:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    motor.move(-25, 25, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    motor.move(25, -25, 0.1)
                else:
                    print('Go straight middle')
                    adjustment_mag(80, 1, magx_off, magy_off)
            elif goalarea <= area_short:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    motor.move(-20, 20, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    motor.move(20, -20, 0.1)
                else:
                    print('Go stright short')
                    adjustment_mag(40, 2, magx_off, magy_off)
            elif goalarea >= G_thd:
                print('goal')
                print('goal')
                break
        print('finish')


    except KeyboardInterrupt:
        print('stop')
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))

if __name__ == "__main__":
    try:
        motor.setup()
        print('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, -40, 30)
        print(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        G_thd = 80
        goalflug = 1
        startTime = time.time()
        dateTime = datetime.datetime.now()
        log_photorunning = '/home/pi/Desktop/Cansat2021ver/log/photorunning_practice.txt'
        path_photo = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'
        image_guided_driving(path_photo, log_photorunning, G_thd, magx_off, magy_off)

    except KeyboardInterrupt:
        print('stop')
        Xbee.off()
    except Exception as e:
        Xbee.off()
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
