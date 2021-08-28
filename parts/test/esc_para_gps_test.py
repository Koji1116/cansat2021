import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/illuminance')
sys.path.append('/home/pi/Desktop/Cansat2021ver/test')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')
import melt
import BMC050
from parts import calibration
import mag
import datetime
# import goaldetection
import photorunning
import glob
# 着地判定後にキャリブレーション前にパラシュート回避を行う
# パラシュート回避エリアは設定せずに、パラシュートが検出されない場合が3回以上(下のプログラムのzで設定)
# のときパラシュート回避を行ったと判定
# そこでキャリブレーションを行い、ローバーをゴール方向に向かせる。
# そのあとにもう一度パラシュート回避を同じ判定方法で行ってGPS走行に移行する。




# --- default module ---#
import time
import traceback
# --- must be installed module ---#
import cv2
# --- original module ---#
# import gps
# import gps_navigate
# import ParaDetection
# import TSL2561
# import goaldetection
import motor
import GPS
import GPS_Navigate
import paradetection

#写真内の赤色面積で進時間を決める用　調整必要
area_short = 100
area_middle = 6
area_long = 1

G_thd = 80  # 調整するところ
goalflug = 1
startTime = time.time()
dateTime = datetime.datetime.now()
path = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'

# --- difine goal latitude and longitude ---#
lon2 = 139.9116179
lat2 = 35.9238862

def escape(t_melt):
    melt.down(t_melt)
    motor.move(20, 20, 0.1)
    # for i in range(5):
    #     strength_l = i * 10
    #     strength_r = i * 10
    #     motor.move(strength_l, strength_r, 0.1)
    # for i in range(5):
    #     strength_l = 50 - i * 10
    #     strength_l = 50 - i * 10
    #     motor.move(strength_l, strength_r, 0.1)


def land_point_save():
    try:
        while True:
            value = GPS.readGPS()
            latitude_land = value[1]
            longitude_land = value[2]
            time.sleep(1)
            if latitude_land != -1.0 and longitude_land != 0.0:
                break
    except KeyboardInterrupt:
        GPS.closeGPS()
        print("\r\nKeyboard Intruppted, Serial Closed")
    except:
        GPS.closeGPS()
        print(traceback.format_exc())
    return longitude_land, latitude_land


def Parachute_area_judge(longitude_land, latitude_land):
    try:
        while True:
            value = GPS.readGPS()
            latitude_new = value[1]
            longitude_new = value[2]
            print(value)
            print('longitude = ' + str(longitude_new))
            print('latitude = ' + str(latitude_new))
            time.sleep(1)
            if latitude_new != -1.0 and longitude_new != 0.0:
                break
    except KeyboardInterrupt:
        GPS.closeGPS()
        print("\r\nKeyboard Intruppted, Serial Closed")

    except:
        GPS.closeGPS()
        print(traceback.format_exc())
    direction = GPS_Navigate.vincenty_inverse(longitude_land, latitude_land, longitude_new, latitude_new)
    distance = direction["distance"]
    return distance


def Parachute_Avoidance(flug, goalGAP):
    # --- There is Parachute around rover ---#

    if flug == 1:
        # --- Avoid parachute by back control ---#
        try:
            # goalflug, goalarea, goalGAP, photoname = photorunning.GoalDetection("photostorage/photostorage_paradete/para",320,240,200,10,120)
            if goalGAP >= -100 and goalGAP <= -50:
                # motor.move(50, -50, 0.1)
                motor.move(70, 70, 1)
                # print('# motor.move(50, -50, 0.1)# motor.move(70, 70, 1)')
            if goalGAP >= -50 and goalGAP <= 0:
                motor.move(50, -50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(80, -80, 1)motor.move(70, 70, 1)')
            if goalGAP >= 0 and goalGAP <= 50:
                motor.move(-50, 50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(-50, 50, 0.1)motor.move(70, 70, 1)')
            if goalGAP >= 50 and goalGAP <= 100:
                # motor.move(-80, 80, 1)
                motor.move(70, 70, 1)
                # print(' # motor.move(-80, 80, 1)# motor.move(70, 70, 1)')

        except KeyboardInterrupt:
            print("stop")
    if flug == -1 or flug == 0:
        # print('flug')
        motor.move(70, 70, 1)

def panorama(srcdir, dstdir, srcprefix='', dstprefix='',srcext='.jpg',dstext='.jpg'):
    """
    パノラマを合成するための関数
    ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
    宛先ディレクトリ内でソースディレクトリ＋番号の形でパノラマ写真が保存される。
    撮影された写真次第ではパノラマ写真をできずエラーが出る可能性あるからtry,except必要？
    srcdir:ソースディレクトリ
    dstdir:宛先ディレクトリ
    prefix:番号の前につける文字
    srcext:ソースの拡張子
    dstext:できたものの拡張子
    """
    srcfilecount = len(glob.glob1(srcdir + '/', '*'+srcext))
    resultcount = len(glob.glob1(dstdir, srcdir + '*'+dstext))
    print(srcfilecount)
    print(resultcount)

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir +'/' + srcprefix + '0' +  str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '/' + srcprefix + str(i) + srcext))




    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)
    cv2.imwrite(dstdir + '/' + dstprefix + str(resultcount) + srcext, result)

    if status == 0:
        print("success")
    else:
        print('failed')


def adjust_direction(theta):
    global magx_off
    global magy_off
    """
    方向調整
    """
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    count = 0
    t_small = 0.1
    t_big = 0.2
    while 15 < theta < 345:

        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1')
            motor.move(20, -20, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2')
            motor.move(20, -20, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3')
            motor.move(-20, 20, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4')
            motor.move(-20, 20, t_big)

        # count += 1
        data = calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = calibration.angle(magx, magy, magx_off, magy_off)
        direction = calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth - theta
        if theta < 0:
            theta = 360 + theta
        elif 360 <= theta <= 450:
            theta = theta - 360
        print('計算後のゴールとなす角度theta' + str(theta))

    print('theta = ' + str(theta) + '---回転終了!!!')





if __name__ == '__main__':
    print('excape start')
    escape(t_melt=3)

    try:
        # print("START: Judge covered by Parachute")
        # TSL2561.tsl2561_setup()
        # t2 = time.time()
        # t1 = t2
        # --- Paracute judge ---#
        # --- timeout is 60s ---#
        # while t2 - t1 < 60:
        # Luxflug = ParaDetection.ParaJudge(10000)
        # print(Luxflug)
        # if Luxflug[0] == 1:
        #	break
        # t1 =time.time()
        # time.sleep(1)
        # print("rover is covered with parachute!")

        print('para avoid start')
        flug, area, gap, photoname = paradetection.paradetection("photostorage/photostorage_paradete/para", 320, 240,
                                                                 200, 10, 120, 1)
        print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
        print("paradetection phase success")
        z = 0
        while z < 3:
            flug, area, gap, photoname = paradetection.paradetection("photostorage/photostorage_paradete/para", 320,
                                                                     240, 200, 10, 120, 1)
            print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
            Parachute_Avoidance(flug, gap)
            print(flug)
            if flug == -1 or flug == 0:
                z += 1
                print(z)

        print("para avoid success")

    except KeyboardInterrupt:
        print("emergency!")

    except:
        print(traceback.format_exc())
    print("finish!")


    print('panorama start')
    try:
        
        srcdir = '/home/pi/Desktop/Cansat2021ver/test/nisho-ground12_640_asyuku'
        dstdir = '/home/pi/Desktop/Cansat2021ver/test/photostorage'
        startTime = time.time()  # プログラムの開始時刻
        panorama(srcdir, dstdir, 'panoramaShootingtest00')
        endTime = time.time() #プログラムの終了時間
        runTime = endTime - startTime
        print(runTime)
    except KeyboardInterrupt:
        print('Interrupted')


    mag.bmc050_setup()
    GPS.openGPS()
    print('GPS走行開始')
    

    # ------------- program start -------------#
    direction = calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    aaa = direction['azimuth1']
    print('goal distance = ' + str(goal_distance))
    print('goal direction = ' + str(aaa))
    count = 0
    while goal_distance >= 10:
        if count % 4 == 0:
            # ------------- calibration -------------#
            print('calibration Start')
            mag.bmc050_setup()
            magdata_Old = calibration.magdata_matrix(20, -20, 0.2, 30)
            _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(magdata_Old)
        print('gps run strat')
        # ------------- gps navigate -------------#
        magdata = BMC050.mag_dataread()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
        direction = calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth - theta
        if theta < 0:
            theta = 360 + theta
        elif 360 <= theta <= 450:
            theta = theta - 360

        adjust_direction(theta)
        print('theta = ' + str(theta) + '---直進開始')
        ######直進するように左の出力強くしてます↓ 7/28 by oosima
        motor.move(65, 50, 6)

        # --- calculate  goal direction ---#
        direction = calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print('------ゴールとの距離は' + str(goal_distance) + 'm------')
        count += 1
    print('!!!!!GPS走行終了。次は画像誘導!!!!!!!!!!!!')

    #-----------photo_run------------#
    G_thd = 80  # 調整するところ
    goalflug = 1
    startTime = time.time()
    dateTime = datetime.datetime.now()
    path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'
    photorunning.image_guided_driving(path_photo_imagerun, 50)