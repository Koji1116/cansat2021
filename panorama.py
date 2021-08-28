import datetime
import cv2
import os
import glob
import time
import shutil
import random

from sensor.camera import capture
from sensor.motor import motor
from sensor.axis import bmc050
import calibration
import paraavoidance
import paradetection
import other


def shooting_angle(theta, path_src_panorama, dict_angle, wid, hig):
    """
    パノラマ合成用の写真を適切な枚数，適切なディレクトリに保存するための関数
    関数shooting内で使用
    """
    switch = True
    # Unpack the dict_angle
    dict_angle1 = dict_angle[0]
    dict_angle2 = dict_angle[1]
    dict_angle3 = dict_angle[2]
    # Unpack the path_src_panorama
    path_src_panorama1 = path_src_panorama[0]
    path_src_panorama2 = path_src_panorama[1]
    path_src_panorama3 = path_src_panorama[2]

    if switch:
        for i in range(12):
            if 30 * i <= theta and theta <= 10 + 30 * i and not dict_angle1[i + 1]:
                capture.Capture(path_src_panorama1, wid, hig)
                dict_angle1[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(12):
            if 10 + 30 * i <= theta and theta <= 20 + 30 * i and not dict_angle2[i + 1]:
                capture.Capture(path_src_panorama2, wid, hig)
                dict_angle2[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(12):
            if 20 + 30 * i <= theta and theta <= 30 + 30 * i and not dict_angle3[i + 1]:
                capture.Capture(path_src_panorama3, wid, hig)
                dict_angle3[i + 1] = True
                break
    return [dict_angle1, dict_angle2, dict_angle3]


def check(dict_angle, path_src_panorama):
    """
    12枚の写真が撮影されたかを判断するための関数
    shooting内で使用
    戻り値はsrcdir
    12枚の写真が撮影された場合は，該当するパス(''じゃない)を返す。elseの場合は''を返す。
    """
    srcdir = ''
    # Unpack the dict_angle
    dict_angle1 = dict_angle[0]
    dict_angle2 = dict_angle[1]
    dict_angle3 = dict_angle[2]
    # Unpack the path_src_panorama
    path_src_panorama1 = path_src_panorama[0]
    path_src_panorama2 = path_src_panorama[1]
    path_src_panorama3 = path_src_panorama[2]
    # Count the number of photos stored in each directory
    number_photos1 = list(dict_angle1.values()).count(True)
    number_photos2 = list(dict_angle2.values()).count(True)
    number_photos3 = list(dict_angle3.values()).count(True)
    # Print number_photos
    print(f'number_photo1:\t{number_photos1}')
    print(f'number_photo2:\t{number_photos2}')
    print(f'number_photo3:\t{number_photos3}')
    # Find a directory/file_name with 12 photos
    srcdir = path_src_panorama1 if number_photos1 == 12 else srcdir
    srcdir = path_src_panorama2 if number_photos2 == 12 else srcdir
    srcdir = path_src_panorama3 if number_photos3 == 12 else srcdir
    # Get the directory name
    rfd = srcdir.rfind('/')
    srcdir = srcdir[:rfd]
    return srcdir


def initialize(path_src_panorama):
    """
    初期化のための関数
    関数shooting内で使用
    引数は撮影した写真のパス
    戻り値はshooting内で使う変数
    """
    # Unpack the path_src_panorama
    path_src_panorama1 = path_src_panorama[0]
    path_src_panorama2 = path_src_panorama[1]
    path_src_panorama3 = path_src_panorama[2]
    # Initialize the directory 1
    rfd1 = path_src_panorama1.rfind('/')
    dir_src_panorama1 = path_src_panorama1[:rfd1]
    shutil.rmtree(dir_src_panorama1)
    os.mkdir(dir_src_panorama1)
    # Initialize the directory 2
    rfd2 = path_src_panorama2.rfind('/')
    dir_src_panorama2 = path_src_panorama2[:rfd2]
    shutil.rmtree(dir_src_panorama2)
    os.mkdir(dir_src_panorama2)
    # Initialize the directory 3
    rfd3 = path_src_panorama3.rfind('/')
    dir_src_panorama3 = path_src_panorama3[:rfd3]
    shutil.rmtree(dir_src_panorama3)
    os.mkdir(dir_src_panorama3)
    # Initializing variables
    count_panorama = 0
    count_stuck = 0
    dict_angle1 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle2 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle3 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle = [dict_angle1, dict_angle2, dict_angle3]
    return count_panorama, count_stuck, dict_angle


def shooting(t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting, wid=320, hig=240):
    """
    パノラマ撮影用の関数
    引数は回転時のモータパワー，1回の回転時間，磁気データ，写真保存用のパス，パラシュート検知のパス，ログ保存用のパス
    スタック判定は角度変化が10度未満が4回あった場合
    スタック時はその場所からパラシュートを確認しながら離れ，やり直す
    スタックによってパノラマ撮影をやり直す回数は3回
    """
    # Initialization by function
    count_panorama, count_stuck, dict_angle = initialize(path_src_panorama)
    # Calculate the angle
    _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(mag_mat)
    magdata = bmc050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0

    # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    # Loop for taking pictures
    while 1:
        dict_angle = shooting_angle(preθ, path_src_panorama, dict_angle, wid, hig)
        srcdir = check(dict_angle, path_src_panorama)
        if srcdir:
            print(f'directory:\t{srcdir}')
            break
        power = random.randint(30, 70)
        strength_l_pano = power
        strength_r_pano = power * -1
        motor.move(strength_l_pano, strength_r_pano, t_rotation_pano, ue=False)
        magdata = bmc050.mag_dataRead()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = calibration.angle(magx, magy, magx_off, magy_off)

        if preθ >= 300 and latestθ <= 100:
            latestθ += 360

        deltaθ = latestθ - preθ

        if 0 <= deltaθ <= 10:
            count_stuck += 1
            # ------Stuck------#
            if count_stuck >= 4:
                count_panorama += 1
                if count_panorama >= 3:
                    break
                count_stuck = 0
                # xbee.str_trans('Stuck')
                print(f'Stuck: {deltaθ}')
                motor.move(60, 60, 0.5, ue=True)
                flug, area, gap, photoname = paradetection.paradetection(path_paradete, 320, 240, 200, 10, 120, 1)
                print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                paraavoidance.Parachute_Avoidance(flug, gap)
                # ----Initialize-----#
                count_panorama, count_stuck, dict_angle = initialize(path_src_panorama)
                magdata = bmc050.mag_dataRead()
                magx = magdata[0]
                magy = magdata[1]
                preθ = calibration.angle(magx, magy, magx_off, magy_off)
                sumθ = 0
                # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print(f'whileスタート　preθ:{preθ}')
                continue

        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print(f'sumθ:\t{sumθ}\tlatestθ\t{latestθ}\tpreθ\t{preθ2}\tdeltaθ\t{deltaθ}\n')
        print(dict_angle[0])
        print('\n')
        print(dict_angle[1])
        print('\n')
        print(dict_angle[2])
        other.saveLog(log_panoramashooting, datetime.datetime.now(), sumθ, latestθ, preθ2, deltaθ)

    return srcdir


def composition(srcdir, srcext='.jpg', dstext='.jpg'):
    """
    パノラマを合成するための関数
    ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
    宛先ディレクトリ内で番号(0~).(拡張子)の形でパノラマ写真が保存される。
    srcdir:ソースディレクトリ
    srcext:ソースの拡張子
    dstext:パノラマ写真の拡張子
    """
    srcfilecount = len(glob.glob1(srcdir, '*' + srcext))
    resultcount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/dst_panorama', '*' + dstext))
    print(f'srcfilecount:\t{srcfilecount}')
    print(f'resultcount:\t{resultcount}')

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir + '/panoramaShooting000' + str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '/panoramaShooting00' + str(i) + srcext))

    print(f'Imreaded photo:\t{len(photos)}')

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(photos)
    if status == 0:
        print('##--Composition succeed--##')

    else:
        print('##--Composition failed--##')
    cv2.imwrite('/home/pi/Desktop/Cansat2021ver/dst_panorama/' + str(resultcount) + '.jpg', result)
    img_name = '/home/pi/Desktop/Cansat2021ver/dst_panorama/' + str(resultcount) + '.jpg'
    print('################################')
    print(f'Panorama name:\t{img_name}')
    print('################################')
    return img_name


if __name__ == "__main__":
    # Initialization
    bmc050.bmc050_setup()
    motor.setup()
    path_src_panorama1 = '/home/pi/Desktop/Cansat2021ver/src_panorama1/panoramaShooting'
    path_src_panorama2 = '/home/pi/Desktop/Cansat2021ver/src_panorama2/panoramaShooting'
    path_src_panorama3 = '/home/pi/Desktop/Cansat2021ver/src_panorama3/panoramaShooting'
    path_src_panorama = (path_src_panorama1, path_src_panorama2, path_src_panorama3)
    path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
    path_paradete = '/home/pi/Desktop/Cansat2021ver/photostorage/paradete'
    log_panoramashooting = other.fileName('/home/pi/Desktop/Cansat2021ver/log/panoramaLog', 'txt')

    mag_mat = calibration.magdata_matrix(40, -40, 60)
    t_rotation_pano = 0.1
    t_start = time.time()
    srcdir = shooting(t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting)
    print(t_start - time.time())
    if input('Composition y/n \t') == 'y':
        t_start = time.time()  # プログラムの開始時刻
        composition(srcdir)
        runTime = time.time() - t_start
        print(runTime)
