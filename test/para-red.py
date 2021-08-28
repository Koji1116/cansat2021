import sys

# sys.path.append('')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/illuminance')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
import time
import cv2
import numpy as np
import other
import Capture
import TSL2572


def ParaJudge(LuxThd):
    '''
    パラシュート被っているかを照度センサを用いて判定する関数
    引数は照度の閾値
    '''
    lux = TSL2572.read()
    # print("lux1: "+str(lux[0]))

    # --- rover is covered with parachute ---#
    if lux < LuxThd:  # LuxThd: 照度センサの閾値
        time.sleep(1)
        return [0, lux]

    # --- rover is not covered with parachute ---#
    else:
        return [1, lux]


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


def ParaDetection(imgpath, width, height, H_min, H_max, S_thd, para_thd, r):
    try:
        imgname = Capture.Capture(imgpath, width, height)
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

        for j in range(len(contours)):
            area = cv2.contourArea(contours[j])
            if max_area < area:
                max_area = area
                max_area_contour = j

        # 最大の赤色の面積を画像全体に対する比率に計算する
        # max_area /= hig * wid
        # max_area *= 100

        centers = get_center(contours[max_area_contour])

        if max_area_contour == -1:
            return [-1, 0, -1, imgname]
        elif max_area >= para_thd:
            max_area /= hig * wid
            max_area *= 100
            gap = (centers[0] - wid / 2) / (wid / 2) * 100
            return [1, max_area, gap, imgname]
        else:
            max_area /= hig * wid
            max_area *= 100
            gap = (centers[0] - wid / 2) / (wid / 2) * 100
            return [0, max_area, gap, imgname]
    except:
        return [0, 100, 100, imgname]


def DrawContours(imgpath, width, height, H_min, H_max, S_thd, r):
    try:
        imgname = Capture.Capture(imgpath, width, height)
        img = cv2.imread(imgname)
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
                (x,y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x),int(y))
                radius = int(radius)
 
                if radius > r:
                    radius_frame = cv2.circle(img,center,radius,(0,0,255),2)
            path = other.fileName("photostorage/para-red", "jpg")
            cv2.imwrite(path ,radius_frame)
            return path
        else:
            path = other.fileName("photostorage/para-red", "jpg")
            return path
    except KeyboardInterrupt:
        print("end drawcircle")





if __name__ == "__main__":
    try:
        x = 1
        while x == 1:
            circle_frame_path = DrawContours("photostorage/photostorage_paradete/para", 320, 240, 200, 10, 120, 1)
            s = input("")
            x = int(s)
            if x != 1:
                break
    except KeyboardInterrupt:
        print("stop drawing circle")



    # TSL2572.tsl2572_setup()
    # --- lux data test ---#
    # try:

    # while 1:
    # ParaJudge(10000)
    # time.sleep(1)

    # except KeyboardInterrupt:
    # print('Stop lux data test')

    # --- Parachute detection test ---#
