import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Casnat2021ver/detection')
import Xbee
import BMC050
import GPS
import motor
from parts import calibration
import time
import mag
import datetime
# import goaldetection
import stuck


#写真内の赤色面積で進時間を決める用　調整必要
area_short = 20
area_middle = 6
area_long = 1

G_thd = 80  # 調整するところ
goalflug = 1
startTime = time.time()
dateTime = datetime.datetime.now()
path = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'


def adjust_direction(theta):
    global magx_off
    global magy_off
    """
    方向調整
    """
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    stuck_count = 1
    t_small = 0.1
    t_big = 0.2
    force = 20 
    while 15 < theta < 345:
        if stuck_count >= 7:
            print('出力強くするよ')
            force +=10
        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1('+str(stuck_count)+'回目)')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2('+str(stuck_count)+'回目)')
            motor.move(force, -force, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3('+str(stuck_count)+'回目)')
            motor.move(-force, force, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4('+str(stuck_count)+'回目)')
            motor.move(-force, force, t_big)
    
        stuck_count += 1
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
        time.sleep(1)

    print('theta = ' + str(theta) + '---回転終了!!!')

if __name__ == "__main__":
    try:
        motor.setup()
        mag.bmc050_setup()
        GPS.openGPS()
        Xbee.on()
        print('Run Phase Start!')
        print('GPS走行開始')
        # --- difine goal latitude and longitude ---#
        
        lon2 = 139.9114415
        lat2 = 35.9236391

        # ------------- program start -------------#
        direction = calibration.calculate_direction(lon2, lat2)
        goal_distance = direction['distance']
        aaa = direction['azimuth1']
        print('goal distance = ' + str(goal_distance))
        print('goal direction = ' + str(aaa))
        count = 0
        ##-----------テスト用--------
        r = float(input('右の出力は？'))
        l = float(input('左の出力は？'))
        t = float(input('何秒回転する？'))
        n = int(input('データ数いくつ'))
        cal = int(input('何回に一回キャリブレーションする？'))
        while goal_distance >= 10:
            if stuck.ue_jug() :
                print('上だよ')
                pass
            else:
                print('したーーーー')
                motor.move(12, 12, 0.2)

            #if count % 4 == 0:
            if count % cal == 0:
                # ------------- calibration -------------#
                print('calibration Start')
                mag.bmc050_setup()
                magdata_Old = calibration.magdata_matrix(l, r, t, n)
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
            GPSdata_old = GPS.GPSdata_read()
            motor.move(50, 50, 6)
            GPSdata_new = GPS.GPSdata_read()
            if stuck.stuck_jug(GPSdata_old[1], GPSdata_old[2], GPSdata_new[1], GPSdata_new[2], 1.0):
                pass
            else:
                #stuck.stuck_avoid()
                print('助けてくださいー')
                time.sleep(8)
                pass
            # --- calculate  goal direction ---#
            direction = calibration.calculate_direction(lon2, lat2)
            goal_distance = direction["distance"]
            print('------ゴールとの距離は' + str(goal_distance) + 'm------')
            count += 1
        print('!!!!!GPS走行終了。次は画像誘導!!!!!!!!!!!!')

        #-----------photo_run------------#
        startTime = time.time()
        dateTime = datetime.datetime.now()
        path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'
        photorunning.image_guided_driving(path_photo_imagerun, 50)
    except KeyboardInterrupt:
        print('interrupted')
        GPS.closeGPS()
    except Exception as e:
        tb = sys.exc_info()[2]
        print(e.with_traceback(tb))
        GPS.closeGPS()
