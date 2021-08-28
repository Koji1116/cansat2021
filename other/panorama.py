import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')

import cv2
import glob
import time
from sensor.motor import motor
from sensor.camera import capture
from sensor.axis import bmc050
import calibration
from sensor.communication import xbee


def composition(srcdir, dstdir, srcext='.jpg', dstext='.jpg'):
    """
    パノラマを合成するための関数
    ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
    宛先ディレクトリ内でソースディレクトリ＋番号の形でパノラマ写真が保存される。
    撮影された写真次第ではパノラマ写真をできずエラーが出る可能性あるからtry,except必要？
    srcdir:ソースディレクトリ
    dstdir:宛先ディレクトリ
    srcext:ソースの拡張子
    dstext:できたものの拡張子
    """
    # try:
    #     srcfilecount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/src_panorama', 'panoramaShooting' + '*' + srcext))
    #     resultcount = len(glob.glob1(dstdir, '*' + dstext))
    #     print(srcfilecount)
    #     print(resultcount)

    #     photos = []

    #     for i in range(0, srcfilecount):
    #         if len(str(i)) == 1:
    #             photos.append(cv2.imread(srcdir + '0' + str(i) + srcext))
    #         else:
    #             photos.append(cv2.imread(srcdir + str(i) + srcext))

    #     print(len(photos))

    #     stitcher = cv2.Stitcher.create(0)
    #     status, result = stitcher.stitch(photos)
    #     if status == 0:
    #         print('composition succeed')

    #     else:
    #         print('composition failed')
    #     cv2.imwrite(dstdir + '/' + str(resultcount) + srcext, result)
    # except Exception as e:
    #     print()
    srcfilecount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/src_panorama', 'panoramaShooting' + '*' + srcext))
    resultcount = len(glob.glob1(dstdir, '*' + dstext))
    print(srcfilecount)
    print(resultcount)

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir + '000' + str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '00' +str(i) + srcext))
    print(photos)
    print(len(photos))

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(photos)
    if status == 0:
        print('composition succeed')

    else:
        print('composition failed')
    #cv2.imwrite(dstdir + '/' + str(resultcount) + srcext, result)
    cv2.imwrite("/home/pi/Desktop/Cansat2021ver/dst_panorama/0.jpg", result)
    
def shooting(l, r, t, mag_mat, path):
    """
    パノラマ撮影用の関数
    引数は磁気のオフセット
    """
    # photobox = []
    _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(mag_mat)
    magdata = bmc050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0
    # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    while sumθ <= 360:
        capture.Capture(path, 960, 540)
        motor.move(l, r, t)
        magdata = bmc050.mag_dataRead()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = calibration.angle(magx, magy, magx_off, magy_off)

        # ------Stuck------#
        if preθ >= 300 and latestθ <= 100:
            latestθ += 360
            if latestθ - preθ <= 10:
                # xbee.str_trans('Stuck')
                print('Stuck')
                motor.move(l, r, t)
                # ----Initialize-----#
                magdata = bmc050.mag_dataRead()
                magx = magdata[0]
                magy = magdata[1]
                preθ = calibration.angle(magx, magy, magx_off, magy_off)
                sumθ = 0
                # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print(f'whileスタート　preθ:{preθ}')
                continue

        if preθ >= 300 and latestθ <= 100:
            latestθ += 360
        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        time.sleep(1)


if __name__ == "__main__":
    # bmc050.BMC050_setup()
    # motor.setup()


    # try:
    #     srcdir = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting'
    #     dstdir = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
        
    #     magdata = calibration.magdata_matrix(40, -40, 0.2, 30)

    #     l = float(input('左の出力'))
    #     r = float(input('右の出力'))
    #     t = float(input('回転時間'))
    #     shooting(l, r, t, magdata, srcdir)
    #     t_start = time.time()  # プログラムの開始時刻
    #     composition(srcdir, dstdir)
    #     runTime = time.time() - t_start
    #     print(runTime)
    # except KeyboardInterrupt:
    #     print('Interrupted')


    srcdir = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting'
    dstdir = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
    
    # magdata = calibration.magdata_matrix(40, -40, 0.2, 30)

    l = float(input('左の出力'))
    #r = float(input('右の出力'))
    t = float(input('回転時間'))
    # shooting(l, -l, t, magdata, srcdir)
    t_start = time.time()  # プログラムの開始時刻
    composition(srcdir, dstdir)
    runTime = time.time() - t_start
    print(runTime)
