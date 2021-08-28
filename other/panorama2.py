import datetime
import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')

import cv2
import os
import glob
import time
import shutil

import motor
import Capture
import BMC050
import calibration
import Xbee
import paraavoidance
import paradetection
import stuck
import other

def composition(srcdir, srcext='.jpg', dstext='.jpg'):
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
    srcfilecount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/src_panorama', 'panoramaShooting' + '*' + srcext))
    resultcount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/dst_panorama', '*' + dstext))
    print(srcfilecount)
    print(resultcount)

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir + '000' + str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '00' + str(i) + srcext))
    print(photos)
    print(len(photos))

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(photos)
    if status == 0:
        print('composition succeed')

    else:
        print('composition failed')
    cv2.imwrite('/home/pi/Desktop/Cansat2021ver/dst_panorama/' + str(resultcount) + '.jpg', result)


def shooting(strength_l_pano, strength_r_pano, t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting, wid=320, hig=240):
    """
    パノラマ撮影用の関数
    引数は回転時のモータパワー，1回の回転時間，磁気データ，写真保存用のパス，パラシュート検知のパス，ログ保存用のパス
    スタック判定は角度変化が10度未満が4回あった場合
    スタック時はその場所からパラシュートを確認しながら離れ，やり直す
    スタックによってパノラマ撮影をやり直す回数は3回
    """
    #initialize
    rfd = path_src_panorama.rfind('/')
    dir_src_panorama = path_src_panorama[:rfd]
    shutil.rmtree(dir_src_panorama)
    os.mkdir(dir_src_panorama)
    count_panorama = 0
    count_stuck = 0

    _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(mag_mat)
    magdata = BMC050.mag_dataread()
    magx = magdata[0]
    magy = magdata[1]
    preθ = calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0
    # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    while sumθ <= 720:
        Capture.Capture(path_src_panorama, wid, hig)
        motor.move(strength_l_pano, strength_r_pano, t_rotation_pano)
        magdata = BMC050.mag_dataread()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = calibration.angle(magx, magy, magx_off, magy_off)

        if preθ >= 300 and latestθ <= 100:
            latestθ += 360


        if latestθ - preθ <= 10:
            count_stuck += 1
            # ------Stuck------#
            if count_stuck >= 4:
                count_panorama += 1
                if count_panorama >= 4:
                    break

                shutil.rmtree(dir_src_panorama)
                os.mkdir(dir_src_panorama)
                count_stuck = 0
                # Xbee.str_trans('Stuck')
                print('Stuck')
                motor.move(60, 60, 0.2)
                flug, area, gap, photoname = paradetection.paradetection(
                    path_paradete, 320, 240, 200, 10, 120, 1)
                print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                paraavoidance.Parachute_Avoidance(flug, gap)
                # ----Initialize-----#
                magdata = BMC050.mag_dataread()
                magx = magdata[0]
                magy = magdata[1]
                preθ = calibration.angle(magx, magy, magx_off, magy_off)
                sumθ = 0
                # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print(f'whileスタート　preθ:{preθ}')
                continue

        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # Xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print(f'sumθ:\t{sumθ}\tlatestθ\t{latestθ}\tpreθ\t{preθ2}\tdeltaθ\t{deltaθ}')
        other.saveLog(log_panoramashooting, datetime.datetime.now(), sumθ, latestθ, preθ2, deltaθ)
        time.sleep(1)


if __name__ == "__main__":
    BMC050.bmc050_setup()
    motor.setup()
    srcdir = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting'
    path_paradete = '/home/pi/Desktop/Cansat2021ver/detection/photostorage/photostorage_paradete/para'
    log_panoramashooting = '/home/pi/Desktop/Cansat2021ver/log/panoramaLog.txt'
    magdata = calibration.magdata_matrix(40, -40, 30)
    power = float(input('モータ出力は？'))
    t = float(input('回転時間は？'))
    shooting(power, -power, t, magdata, srcdir, path_paradete, log_panoramashooting)
    t_start = time.time()  # プログラムの開始時刻
    composition(srcdir)
    runTime = time.time() - t_start
    print(runTime)
