import time
import datetime
import sys

import release
import paradetection
import land
import paraavoidance
from sensor.axis import bmc050
from sensor.communication import xbee
from sensor.gps import gps
from sensor.motor import motor
from sensor.envirionmental import bme280
import panorama
import other
import escape
import gpsrunning
import photorunning
from . import calibration
dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 5
t_out_land = 5

# variable for release
thd_press_release = 0.3
t_delta_release = 1

# variable for landing
thd_press_land = 0.15

# variable for calibration
strength_l_cal = 40
strength_r_cal = -40
t_rotation_cal = 0.2
number_data = 30

# variable for panorama
strength_l_pano = 33
strength_r_pano = -33
t_rotation_pano = 0.1

# variable for GPSrun
lat2 = 35.9235821
lon2 = 139.9118476

th_distance = 6.5
t_adj_gps = 180

# variable for photorun
G_thd = 80
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# variable for log
log_phase = other.fileName('/home/pi/Desktop/cansat2021/log/phaseLog', 'txt')
log_release = other.fileName('/home/pi/Desktop/cansat2021/log/releaselog', 'txt')
log_landing = other.fileName('/home/pi/Desktop/cansat2021/log/landingLog', 'txt')
log_melting = other.fileName('/home/pi/Desktop/cansat2021/log/meltingLog', 'txt')
log_paraavoidance = other.fileName('/home/pi/Desktop/cansat2021/log/paraAvoidanceLog', 'txt')
log_panoramashooting = other.fileName('/home/pi/Desktop/cansat2021/log/panoramaLog', 'txt')
log_gpsrunning = other.fileName('/home/pi/Desktop/cansat2021/log/gpsrunningLog', 'txt')
log_photorunning = other.fileName('/home/pi/Desktop/cansat2021/log/photorunning', 'txt')
log_panoramacom = other.fileName('/home/pi/Desktop/cansat2021/log/panoramacomLog', 'txt')

# photo path
path_src_panorama1 = '/home/pi/Desktop/cansat2021/src_panorama1/panoramaShooting'
path_src_panorama2 = '/home/pi/Desktop/cansat2021/src_panorama2/panoramaShooting'
path_src_panorama3 = '/home/pi/Desktop/cansat2021/src_panorama3/panoramaShooting'
path_src_panorama = (path_src_panorama1, path_src_panorama2, path_src_panorama3)
path_paradete = '/home/pi/Desktop/cansat2021/photostorage/paradete'


def setup():
    global phaseChk
    xbee.on()
    gps.openGPS()
    bmc050.bmc050_setup()
    bme280.bme280_setup()
    bme280.bme280_calib_param()


def close():
    gps.closeGPS()
    xbee.off()


if __name__ == '__main__':

    # remove file
    # iino = input('本当に写真ファイル削除していい？git pullした？[y/n]')
    # if iino == "y":
    #     os.remove('/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting*jpg')
    #     os.remove('/home/pi/Desktop/Cansat2021ver/dst_panorama/*')
    #     print('removed')
    # else:
    #     pass
    # close()
    motor.setup()

    #######-----------------------Setup--------------------------------#######

    try:
        t_start = time.time()
        print('#####-----Setup Phase start-----#####')
        other.saveLog(log_phase, "1", "Setup phase", dateTime, time.time() - t_start)
        phaseChk = other.phaseCheck(log_phase)
        if phaseChk == 1:
            print(f'Phase:\t{phaseChk}')
            setup()
            print('#####-----Setup Phase ended-----##### \n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(setup)-----#####')
        print('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Release--------------------------#######
    print('#####-----Release Phase start-----#####')
    other.saveLog(log_phase, "2", "Release Phase Started", dateTime, time.time() - t_start)
    phaseChk = other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    if phaseChk == 2:
        t_release_start = time.time()
        i = 1
        try:
            while time.time() - t_release_start <= t_out_release:
                print(f'loop_release\t {i}')
                press_count_release, press_judge_release = release.pressdetect_release(thd_press_release, t_delta_release)
                print(f'count:{press_count_release}\tjudge{press_judge_release}')
                other.saveLog(log_release, dateTime, time.time() - t_start, gps.GPSdata_read(),
                              bme280.bme280_read(), press_count_release, press_judge_release)
                if press_judge_release == 1:
                    print('Release\n \n')
                    break
                else:
                    print('Not Release\n \n')
                i += 1
            else:
                print('##--release timeout--##')
            print("######-----Released-----##### \n \n")
        except Exception as e:
            tb = sys.exc_info()[2]
            print("message:{0}".format(e.with_traceback(tb)))
            print('#####-----Error(Release)-----#####')
            print('#####-----Error(Release)-----#####\n \n')

    #######--------------------------Landing--------------------------#######
    try:
        print('#####-----Landing phase start-----#####')
        other.saveLog(log_phase, '3', 'Landing phase', dateTime, time.time() - t_start)
        phaseChk = other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
            print(f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                print(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(thd_press_land)
                print(f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    print('Landed\n \n')
                    break
                else:
                    print('Not Landed\n \n')
                other.saveLog(log_landing, dateTime, time.time() - t_start, gps.GPSdata_read(), bme280.bme280_read())
                i += 1
            else:
                print('Landed Timeout')
            other.saveLog(log_landing, dateTime, time.time() - t_start, gps.GPSdata_read(), bme280.bme280_read(),
                          'Land judge finished')
            print('######-----Landed-----######\n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(Landing)-----#####')
        print('#####-----Error(Landing)-----#####\n \n')
    # #######-----------------------------------------------------------########

    #######--------------------------Escape--------------------------#######

    print('#####-----Melting phase start#####')
    other.saveLog(log_phase, '4', 'Melting phase start', dateTime, time.time() - t_start)
    phaseChk = other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    if phaseChk == 4:
        other.saveLog(log_melting, dateTime, time.time() - t_start, gps.GPSdata_read(), "Melting Start")
        escape.escape()
        other.saveLog(log_melting, dateTime, time.time() - t_start, gps.GPSdata_read(), "Melting Finished")
    print('########-----Melted-----#######\n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print("message:{0}".format(e.with_traceback(tb)))
    #     print('#####-----Error(melting)-----#####')
    #     print('#####-----Error(melting)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Paraavo--------------------------#######

    print('#####-----Para avoid start-----#####')
    other.saveLog(log_phase, '5', 'Melting phase start', dateTime, time.time() - t_start)
    phaseChk = other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    count_paraavo = 0
    if phaseChk == 5:
        while count_paraavo < 2:
            flug, area, gap, photoname = paradetection.paradetection(
                path_paradete, 320, 240, 200, 10, 120, 1)
            print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
            other.saveLog(log_paraavoidance, dateTime, time.time() - t_start, gps.GPSdata_read(), flug, area, gap, photoname)
            paraavoidance.Parachute_Avoidance(flug, gap)
            time.sleep(1)
            if flug == -1 or flug == 0:
                count_paraavo += 1
    print('#####-----ParaAvo Phase ended-----##### \n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print("message:{0}".format(e.with_traceback(tb)))
    #     print('#####-----Error(paraavo)-----#####')
    #     print('#####-----Error(paraavo)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------panorama--------------------------#######

    print('#####-----panorama shooting start-----#####')
    other.saveLog(log_phase, '6', 'panorama shooting phase start', dateTime, time.time() - t_start)
    phaseChk = other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    if phaseChk == 6:
        t_start_panorama = time.time()  # プログラムの開始時刻
        time.sleep(3)
        mag_mat = calibration.magdata_matrix(strength_l_cal, strength_r_cal, number_data)
        path_src_panorama = panorama.shooting(t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting)
        print(f'runTime_panorama:\t{time.time() - t_start_panorama}')
    print('#####-----panorama ended-----##### \n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print("message:{0}".format(e.with_traceback(tb)))
    #     print('#####-----Error(panorama)-----#####')
    #     print('#####-----Error(panorama)-----#####\n \n')
    # #######-----------------------------------------------------------########

    ####-----goal-parachute-roverの位置関係の場合のためのパラ回避-----#####
    magx_off, magy_off = calibration.cal(40, -40, 30)
    gpsrunning.adjust_direction(gpsrunning.angle_goal(magx_off, magy_off, lon2, lat2), magx_off, magy_off, lon2, lat2)
    count_paraavo2 = 0
    while count_paraavo2 < 3:
        flug, area, gap, photoname = paradetection.paradetection(
            path_paradete, 320, 240, 200, 10, 120, 1)
        print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
        other.saveLog(log_paraavoidance, dateTime, time.time() - t_start, gps.GPSdata_read(), flug, area, gap, photoname)
        paraavoidance.Parachute_Avoidance(flug, gap)
        time.sleep(1)
        if flug == -1 or flug == 0:
            count_paraavo2 += 1

    #######--------------------------gps--------------------------#######

    print('#####-----gps run start-----#####')
    other.saveLog(log_phase, '7', 'GPSrun phase start', dateTime, time.time() - t_start)
    phaseChk = other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    if phaseChk == 7:
        gpsrunning.drive(lon2, lat2, th_distance, t_adj_gps, log_gpsrunning)
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print("message:{0}".format(e.with_traceback(tb)))
    #     print('#####-----Error(gpsrunning)-----#####')
    #     print('#####-----Error(gpsrunning)-----#####\n \n')

    ######------------------photo running---------------------##########
    try:
        print('#####-----photo run start-----#####')
        other.saveLog(log_phase, '8', 'image run phase start', dateTime, time.time() - t_start)
        phaseChk = other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 8:
            magx_off, magy_off = calibration.cal(40, -40, 60)
            photorunning.image_guided_driving(log_photorunning, G_thd, magx_off, magy_off, lon2, lat2, th_distance, t_adj_gps, gpsrun=True)
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(Photo running)-----#####')
        print('#####-----Error(Photo running)-----#####\n \n')

    #####------------------panorama composition--------------##########
    try:
        con = input('continue?y/n\t')
        if con == 'n':
            exit()
        print('#####-----panorama composition-----#####')
        other.saveLog(log_phase, '9', 'panorama composition phase start', dateTime, time.time() - t_start)
        phaseChk = other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 9:
            # Create a panoramic photo
            t_composition_start = time.time()
            img1 = panorama.composition(path_src_panorama)
            print(time.time() - t_composition_start)
            # Sending a panoramic photo
            img_string = xbee.ImageToByte(img1)
            xbee.img_trans(img_string)
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(panorama composition)-----#####')
        print('#####-----Error(panorama composition)-----#####\n \n')
