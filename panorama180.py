import datetime
import cv2
import os
import glob
import time
import shutil
import random
import numpy as np

from sensor.camera import take
from sensor.axis import bmc050
from sensor.communication import xbee
from other import print_xbee
import calibration
import paraavoidance
import paradetection
import motor
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
    dict_angle4 = dict_angle[3]
    dict_angle5 = dict_angle[4]
    dict_angle6 = dict_angle[5]

    # Unpack the path_src_panorama
    path_src_panorama1 = path_src_panorama[0]
    path_src_panorama2 = path_src_panorama[1]
    path_src_panorama3 = path_src_panorama[2]
    path_src_panorama4 = path_src_panorama[3]
    path_src_panorama5 = path_src_panorama[4]
    path_src_panorama6 = path_src_panorama[5]


    if switch:
        for i in range(6):
            if 30 * i <= theta and theta <= 10 + 30 * i and not dict_angle1[i + 1]:
                take.picture(path_src_panorama1, wid, hig)
                dict_angle1[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(6):
            if 10 + 30 * i <= theta and theta <= 20 + 30 * i and not dict_angle2[i + 1]:
                take.picture(path_src_panorama2, wid, hig)
                dict_angle2[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(6):
            if 20 + 30 * i <= theta and theta <= 30 + 30 * i and not dict_angle3[i + 1]:
                take.picture(path_src_panorama3, wid, hig)
                dict_angle3[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(6, 12):
            if 30 * i <= theta and theta <= 10 + 30 * i and not dict_angle4[i + 1]:
                take.picture(path_src_panorama1, wid, hig)
                dict_angle1[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(6, 12):
            if 10 + 30 * i <= theta and theta <= 20 + 30 * i and not dict_angle5[i + 1]:
                take.picture(path_src_panorama2, wid, hig)
                dict_angle2[i + 1] = True
                switch = False
                break
    if switch:
        for i in range(6, 12):
            if 20 + 30 * i <= theta and theta <= 30 + 30 * i and not dict_angle6[i + 1]:
                take.picture(path_src_panorama3, wid, hig)
                dict_angle3[i + 1] = True
                switch = False
                break
    return [dict_angle1, dict_angle2, dict_angle3, dict_angle4, dict_angle5, dict_angle6]


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
    dict_angle4 = dict_angle[3]
    dict_angle5 = dict_angle[4]
    dict_angle6 = dict_angle[5]

    # Unpack the path_src_panorama
    path_src_panorama1 = path_src_panorama[0]
    path_src_panorama2 = path_src_panorama[1]
    path_src_panorama3 = path_src_panorama[2]
    path_src_panorama4 = path_src_panorama[3]
    path_src_panorama5 = path_src_panorama[4]
    path_src_panorama6 = path_src_panorama[5]

    # Count the number of photos stored in each directory
    number_photos1 = list(dict_angle1.values()).count(True)
    number_photos2 = list(dict_angle2.values()).count(True)
    number_photos3 = list(dict_angle3.values()).count(True)
    number_photos4 = list(dict_angle4.values()).count(True)
    number_photos5 = list(dict_angle5.values()).count(True)
    number_photos6 = list(dict_angle6.values()).count(True)

    # Print number_photos
    print_xbee(f'number_photo1:\t{number_photos1}')
    print_xbee(f'number_photo2:\t{number_photos2}')
    print_xbee(f'number_photo3:\t{number_photos3}')
    print_xbee(f'number_photo4:\t{number_photos4}')
    print_xbee(f'number_photo5:\t{number_photos5}')
    print_xbee(f'number_photo6:\t{number_photos6}')

    # Find a directory/file_name with 12 photos
    srcdir = path_src_panorama1 if number_photos1 == 12 else srcdir
    srcdir = path_src_panorama2 if number_photos2 == 12 else srcdir
    srcdir = path_src_panorama3 if number_photos3 == 12 else srcdir
    srcdir = path_src_panorama4 if number_photos4 == 12 else srcdir
    srcdir = path_src_panorama5 if number_photos5 == 12 else srcdir
    srcdir = path_src_panorama6 if number_photos6 == 12 else srcdir

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
    path_src_panorama4 = path_src_panorama[3]
    path_src_panorama5 = path_src_panorama[4]
    path_src_panorama6 = path_src_panorama[5]

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
    # Initialize the directory 4
    rfd4 = path_src_panorama4.rfind('/')
    dir_src_panorama4 = path_src_panorama4[:rfd4]
    shutil.rmtree(dir_src_panorama4)
    os.mkdir(dir_src_panorama4)
    # Initialize the directory 5
    rfd5 = path_src_panorama5.rfind('/')
    dir_src_panorama5 = path_src_panorama5[:rfd5]
    shutil.rmtree(dir_src_panorama5)
    os.mkdir(dir_src_panorama5)
    # Initialize the directory 6
    rfd6 = path_src_panorama6.rfind('/')
    dir_src_panorama6 = path_src_panorama6[:rfd6]
    shutil.rmtree(dir_src_panorama6)
    os.mkdir(dir_src_panorama6)

    # Initializing variables
    count_panorama = 0
    count_stuck = 0
    dict_angle1 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle2 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle3 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle4 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle5 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle6 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle = [dict_angle1, dict_angle2, dict_angle3, dict_angle4, dict_angle5, dict_angle6]
    return count_panorama, count_stuck, dict_angle

def azimuth(magx_off, magy_off, n=1):
    theta = []

    for i in range(n):
        time.sleep(0.02)
        magdata = bmc050.mag_read()
        magx = magdata[0]
        magy = magdata[1]
        theta = np.append(theta, calibration.angle(magx, magy, magx_off, magy_off))
    print(theta)
    azimuth = np.average(theta)
    return azimuth


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
    preθ = azimuth(magx_off, magy_off)
    sumθ = 0

    # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print_xbee(f'whileスタート　preθ:{preθ}')

    # Loop for taking pictures
    while 1:
        dict_angle = shooting_angle(preθ, path_src_panorama, dict_angle, wid, hig)
        srcdir = check(dict_angle, path_src_panorama)
        if srcdir:
            print_xbee(f'directory:\t{srcdir}')
            break
        power = random.randint(25, 75)
        strength_l_pano = power
        strength_r_pano = power * -1
        motor.move(strength_l_pano, strength_r_pano, t_rotation_pano, ue=False)
        latestθ = azimuth(magx_off, magy_off)

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
                print_xbee(f'Stuck: {deltaθ}')
                motor.move(60, 60, 0.5, ue=True)
                flug, area, gap, photoname = paradetection.para_detection(path_paradete, 320, 240, 200, 10, 120, 1)
                print_xbee(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                paraavoidance.parachute_avoidance(flug, gap)
                # ----Initialize-----#
                count_panorama, count_stuck, dict_angle = initialize(path_src_panorama)
                preθ = azimuth(magx_off, magy_off)
                sumθ = 0
                # xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print_xbee(f'whileスタート　preθ:{preθ}')
                continue

        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print_xbee(f'sumθ:\t{sumθ}\tlatestθ\t{latestθ}\tpreθ\t{preθ2}\tdeltaθ\t{deltaθ}\n')
        print_xbee('\n')
        print_xbee('\n')
        other.log(log_panoramashooting, datetime.datetime.now(), sumθ, latestθ, preθ2, deltaθ)
        time.sleep(0.2)
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
    resultcount = len(glob.glob1('/home/pi/Desktop/cansat2021ver/dst_panorama', '*' + dstext))
    print_xbee(f'srcfilecount:\t{srcfilecount}')
    print_xbee(f'resultcount:\t{resultcount}')

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir + '/panoramaShooting000' + str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '/panoramaShooting00' + str(i) + srcext))

    print_xbee(f'Imreaded photo:\t{len(photos)}')

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(photos)
    if status == 0:
        print_xbee('##--Composition succeed--##')

    else:
        print_xbee('##--Composition failed--##')
    path_dst = other.filename('/home/pi/Desktop/cansat2021/dst_panorama/dst', 'jpg')
    cv2.imwrite(path_dst, result)
    print_xbee('###################################################################')
    print_xbee(f'Panorama name:\t{path_dst}')
    print_xbee('###################################################################')
    return path_dst


if __name__ == "__main__":
    # Initialization
    bmc050.bmc050_setup()
    motor.setup()
    xbee.on()
    path_src_panorama1 = '/home/pi/Desktop/cansat2021ver/src_panorama1/panoramaShooting'
    path_src_panorama2 = '/home/pi/Desktop/cansat2021ver/src_panorama2/panoramaShooting'
    path_src_panorama3 = '/home/pi/Desktop/cansat2021ver/src_panorama3/panoramaShooting'
    path_src_panorama4 = '/home/pi/Desktop/cansat2021ver/src_panorama4/panoramaShooting'
    path_src_panorama5 = '/home/pi/Desktop/cansat2021ver/src_panorama5/panoramaShooting'
    path_src_panorama6 = '/home/pi/Desktop/cansat2021ver/src_panorama6/panoramaShooting'
    
    path_src_panorama = (path_src_panorama1, path_src_panorama2, path_src_panorama3,
                        path_src_panorama4, path_src_panorama5, path_src_panorama6)
    path_dst_panorama = '/home/pi/Desktop/cansat2021ver/dst_panorama'
    path_paradete = '/home/pi/Desktop/cansat2021ver/photostorage/paradete'
    log_panoramashooting = other.filename('/home/pi/Desktop/cansat2021ver/log/panoramaLog', 'txt')
    
    for i in range(0, 6):
        other.make_dir("path_src_panorama"+i)
    other.make_dir(path_src_panorama)
    other.make_dir(path_dst_panorama)
    mag_mat = calibration.magdata_matrix(40, -40, 30)
    t_rotation_pano = 0.1
    t_start = time.time()
    srcdir = shooting(t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting)
    print_xbee(time.time() - t_start)
    if input('Composition y/n \t') == 'y':
        t_start = time.time()  # プログラムの開始時刻
        composition(srcdir)
        runTime = time.time() - t_start
        print_xbee(runTime)
