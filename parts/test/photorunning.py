import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
import cv2
import numpy as np
import Capture
# import stuck
import Xbee
import motor
from parts import other
import datetime
import time

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
            return [1, 0, 1000, imgname]
        elif max_area <= 0.4:
            return [1, max_area, 1000000, imgname]
        elif max_area >= G_thd:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [0, max_area, GAP, imgname]
        else:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [1, max_area, GAP, imgname]
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


def image_guided_driving(path, G_thd):
    goalflug = 1
    try:
        while goalflug != 0:
            # if stuck.ue_jug() :
            #     pass
            # else:
            #     motor.move(12, 12, 0.2)
            photoName = Capture.Capture(path)  # 解像度調整するところ？
            goalflug, goalarea, gap, imgname = GoalDetection(photoName, 200, 20, 80, 50)
            imgname2 = DrawContours(imgname, 200, 20, 80)
            print(f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}\timagename:{imgname}\timagename2:{imgname2}')
            # other.saveLog(path,startTime - time.time(), goalflug, goalarea, goalGAP)
            if gap == 1000 or gap == 1000000:
                print('Nogoal detected')
                motor.move(40, -40, 0.1)
            elif goalarea <= area_long:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    # print('Turn left')
                    motor.move(-40, 40, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    # print('Turn right')
                    motor.move(40, -40, 0.1)
                else:
                    print('Go straight long')
                    print('GO straight long')
                    motor.move(80, 80, 3)
            elif goalarea <= area_middle:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    # print('Turn left')
                    motor.move(-25, 25, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    # print('Turn right')
                    motor.move(25, -25, 0.1)
                else:
                    print('Go straight middle')
                    # print('Go straight middle')
                    motor.move(80, 80, 1)
            elif goalarea <= area_short:
                if -100 <= gap and gap <= -65:
                    print('Turn left')
                    # print('Turn left')
                    motor.move(-15, 15, 0.1)
                elif 65 <= gap and gap <= 100:
                    print('Turn right')
                    # print('Turn right')
                    motor.move(15, -15, 0.1)
                else:
                    print('Go stright short')
                    # print('Gos straight short')
                    motor.move(40, 40, 0.2)
            elif goalarea >= G_thd:
                print('goal')
                print('goal')
                break
        print('finish')
        print('finish')


    except KeyboardInterrupt:
        print('stop')
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))


if __name__ == "__main__":
    try:
        # G_thd = float(input('ゴール閾値'))
        motor.setup()
        G_thd = 80  # 調整するところ
        goalflug = 1
        startTime = time.time()
        dateTime = datetime.datetime.now()
        path = f'photostorage/ImageGuidance2_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'
        image_guided_driving(path, G_thd)

        # photoName = 'photostorage/practice13.png'
        # while goalflug != 0:
        #     photoName = Capture.Capture(path, 320, 320)                                               #解像度調整するところ？
        #     goalflug, goalarea, gap, imgname = GoalDetection(photoName, 200, 20, 80, 50)
        #     print(f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}\timagename:{imgname}')
        #     # print('goalflug', goalflug, ' goalarea', goalarea, ' goalGAP', goalGAP)
        #     # other.saveLog(path,startTime - time.time(), goalflug, goalarea, goalGAP)
        #     if -100 <= gap and gap <= -65:                                                                                  #調整するところ
        #         print('Turn left')
        #         # print('Turn left')
        #         motor.move(-40, 40, 0.1)                                                       #調整するところ
        #         # print('motor.motor(-0.2, 0.2, 0.3)')
        #     elif 65 <= gap and gap <= 100:
        #         print('Turn right')
        #         # print('Turn right')
        #         motor.move(40, -40, 0.1)                                                       #調整するところ
        #         # print('motor.motor(0.2, -0.2, 0.3)')
        #     elif gap == 1000 or gap==1000000:
        #         print('Nogoal detected')
        #         motor.move(40, -40, 0.1)                                                       #調整するところ
        #         # print('motor.motor(0.2, -0.2, 0.5)')
        #     else:
        #         print('Go straight')
        #         if goalarea <= area_long:
        #             motor.move(80, 80, 3)                                                        #調整するところ
        #             # print('motor.motor(1, 1, 10)')
        #             print('long')
        #         elif goalarea <= area_middle:
        #             motor.move(80, 80, 1)                                                        #調整するところ
        #             # print('motor.motor(1, 1, 5)')
        #             print('middle')
        #         elif goalarea <= area_short:
        #             motor.move(80, 80, 0.2)                                                      #調整するところ
        #             # print('motor.motor(1, 1, 2)')
        #             print('short')


    except KeyboardInterrupt:
        print('stop')
        Xbee.off()
    except Exception as e:
        Xbee.off()
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
