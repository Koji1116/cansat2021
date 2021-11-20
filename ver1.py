import time
import datetime
import sys

from sensor.axis import bmc050
from sensor.communication import xbee
from sensor.gps import gps
from sensor.envirionmental import bme280
from other import print_xbee
import release
import paradetection
import land
import paraavoidance
import panorama
import panorama180
import other
import escape
import gpsrunning
import photorunning
import calibration
import motor

dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 360
t_out_land = 60

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
# lat2 = 35.918548
# lon2 = 139.908896
lat2 = 35.412957
lon2 = 138.592717

th_distance = 6.5
t_adj_gps = 180

# variable for photorun
G_thd = 50
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# variable for log
log_phase = other.filename('/home/pi/Desktop/cansat2021/log/phaseLog', 'txt')
log_release = other.filename(
    '/home/pi/Desktop/cansat2021/log/releaselog', 'txt')
log_landing = other.filename(
    '/home/pi/Desktop/cansat2021/log/landingLog', 'txt')
log_melting = other.filename(
    '/home/pi/Desktop/cansat2021/log/meltingLog', 'txt')
log_paraavoidance = other.filename(
    '/home/pi/Desktop/cansat2021/log/paraAvoidanceLog', 'txt')
log_panoramashooting = other.filename(
    '/home/pi/Desktop/cansat2021/log/panoramaLog', 'txt')
log_gpsrunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/gpsrunningLog', 'txt')
log_photorunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/photorunning', 'txt')
log_panoramacom = other.filename(
    '/home/pi/Desktop/cansat2021/log/panoramacomLog', 'txt')

# photo path
path_src_panorama1 = '/home/pi/Desktop/cansat2021/src_panorama1/panoramaShooting'
path_src_panorama2 = '/home/pi/Desktop/cansat2021/src_panorama2/panoramaShooting'
path_src_panorama3 = '/home/pi/Desktop/cansat2021/src_panorama3/panoramaShooting'
path_src_panorama4 = '/home/pi/Desktop/cansat2021/src_panorama4/panoramaShooting'
path_src_panorama5 = '/home/pi/Desktop/cansat2021/src_panorama5/panoramaShooting'
path_src_panorama6 = '/home/pi/Desktop/cansat2021/src_panorama6/panoramaShooting'
path_src_panorama = (path_src_panorama1, path_src_panorama2, path_src_panorama3,
                     path_src_panorama4, path_src_panorama5, path_src_panorama6)
path_paradete = '/home/pi/Desktop/cansat2021/photo_paradete/paradete'


def setup():
    global phase
    xbee.on()
    gps.open_gps()
    bmc050.bmc050_setup()
    bme280.bme280_setup()
    bme280.bme280_calib_param()


def close():
    gps.close_gps()
    xbee.off()


if __name__ == '__main__':
    motor.setup()

    #######-----------------------Setup--------------------------------#######
    try:
        t_start = time.time()
        print_xbee('#####-----Setup Phase start-----#####')
        other.log(log_phase, "1", "Setup phase",
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        if phase == 1:
            print_xbee(f'Phase:\t{phase}')
            setup()
            print_xbee('#####-----Setup Phase ended-----##### \n \n')
            print_xbee('####----wait----#### ')
            for i in range(10):
                print_xbee(i)
                time.sleep(1)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(setup)-----#####')
        print_xbee('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Release--------------------------#######
    print_xbee('#####-----Release Phase start-----#####')
    other.log(log_phase, "2", "Release Phase Started",
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 2:
        t_release_start = time.time()
        i = 1
        try:
            while time.time() - t_release_start <= t_out_release:
                print_xbee(f'loop_release\t {i}')
                press_count_release, press_judge_release = release.pressdetect_release(
                    thd_press_release, t_delta_release)
                print_xbee(
                    f'count:{press_count_release}\tjudge{press_judge_release}')
                other.log(log_release, datetime.datetime.now(), time.time() - t_start, gps.gps_data_read(),
                          bme280.bme280_read(), press_count_release, press_judge_release)
                if press_judge_release == 1:
                    print_xbee('Release\n \n')
                    break
                else:
                    print_xbee('Not Release\n \n')
                i += 1
            else:
                print_xbee('##--release timeout--##')
            print_xbee("######-----Released-----##### \n \n")
        except Exception as e:
            tb = sys.exc_info()[2]
            print_xbee("message:{0}".format(e.with_traceback(tb)))
            print_xbee('#####-----Error(Release)-----#####')
            print_xbee('#####-----Error(Release)-----#####\n \n')

    #######--------------------------Landing--------------------------#######
    try:
        print_xbee('#####-----Landing phase start-----#####')
        other.log(log_phase, '3', 'Landing phase',
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        if phase == 3:
            print_xbee(
                f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                print_xbee(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(
                    thd_press_land)
                print_xbee(
                    f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    print_xbee('Landed\n \n')
                    break
                else:
                    print_xbee('Not Landed\n \n')
                other.log(log_landing, datetime.datetime.now(), time.time() - t_start,
                          gps.gps_data_read(), bme280.bme280_read())
                i += 1
            else:
                print_xbee('Landed Timeout')
            other.log(log_landing, datetime.datetime.now(), time.time() - t_start, gps.gps_data_read(), bme280.bme280_read(),
                      'Land judge finished')
            print_xbee('######-----Landed-----######\n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(Landing)-----#####')
        print_xbee('#####-----Error(Landing)-----#####\n \n')
    # #######-----------------------------------------------------------########

    #######--------------------------Escape--------------------------#######

    print_xbee('#####-----Melting phase start#####')
    other.log(log_phase, '4', 'Melting phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 4:
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Melting Start")
        escape.escape()
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Melting Finished")
    print_xbee('########-----Melted-----#######\n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(melting)-----#####')
    #     print_xbee('#####-----Error(melting)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Paraavo--------------------------#######

    print_xbee('#####-----Para avoid start-----#####')
    other.log(log_phase, '5', 'Paraavo phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    count_paraavo = 0
    if phase == 5:
        while count_paraavo < 3:
            flug, area, gap, photoname = paradetection.para_detection(
                path_paradete, 320, 240, 200, 10, 120, 1)
            print_xbee(
                f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
            other.log(log_paraavoidance, datetime.datetime.now(), time.time() -
                      t_start, gps.gps_data_read(), flug, area, gap, photoname)
            paraavoidance.parachute_avoidance(flug, gap)
            if flug == -1 or flug == 0:
                count_paraavo += 1
    print_xbee('#####-----ParaAvo Phase ended-----##### \n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(paraavo)-----#####')
    #     print_xbee('#####-----Error(paraavo)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------panorama--------------------------#######

    print_xbee('#####-----panorama shooting start-----#####')
    other.log(log_phase, '6', 'panorama shooting phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 6:
        t_start_panorama = time.time()  # プログラムの開始時刻
        time.sleep(3)
        mag_mat = calibration.magdata_matrix(
            strength_l_cal, strength_r_cal, number_data)
        path_src_panorama = panorama180.shooting(
            t_rotation_pano, mag_mat, path_src_panorama, path_paradete, log_panoramashooting)
        print_xbee(f'runTime_panorama:\t{time.time() - t_start_panorama}')
    print_xbee('#####-----panorama ended-----##### \n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(panorama)-----#####')
    #     print_xbee('#####-----Error(panorama)-----#####\n \n')
    # #######-----------------------------------------------------------########

    ####-----goal-parachute-roverの位置関係の場合のためのパラ回避-----#####
    magx_off, magy_off = calibration.cal(40, -40, 30)
    gpsrunning.adjust_direction(gpsrunning.angle_goal(
        magx_off, magy_off, lon2, lat2), magx_off, magy_off, lon2, lat2)
    count_paraavo2 = 0
    while count_paraavo2 < 4:
        flug, area, gap, photoname = paradetection.para_detection(
            path_paradete, 320, 240, 200, 10, 120, 1)
        print_xbee(
            f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
        other.log(log_paraavoidance, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), flug, area, gap, photoname)
        paraavoidance.parachute_avoidance(flug, gap)
        if flug == -1 or flug == 0:
            count_paraavo2 += 1

    #######--------------------------gps--------------------------#######

    print_xbee('#####-----gps run start-----#####')
    other.log(log_phase, '7', 'GPSrun phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 7:
        gpsrunning.drive(lon2, lat2, th_distance, t_adj_gps, log_gpsrunning)
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(gpsrunning)-----#####')
    #     print_xbee('#####-----Error(gpsrunning)-----#####\n \n')

    ######------------------photo running---------------------##########
    try:
        print_xbee('#####-----photo run start-----#####')
        other.log(log_phase, '8', 'image run phase start',
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        if phase == 8:
            magx_off, magy_off = calibration.cal(40, -40, 60)
            photorunning.image_guided_driving(
                log_photorunning, G_thd, magx_off, magy_off, lon2, lat2, th_distance, t_adj_gps, gpsrun=True)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(Photo running)-----#####')
        print_xbee('#####-----Error(Photo running)-----#####\n \n')

    #####------------------panorama composition--------------##########
    try:

        print_xbee('#####-----panorama composition-----#####')
        other.log(log_phase, '9', 'panorama composition phase start',
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        if phase == 9:
            # Create a panoramic photo
            t_composition_start = time.time()
            img1 = panorama.composition(path_src_panorama)
            print_xbee(time.time() - t_composition_start)
            # Sending a panoramic photo
            # 画像伝送するために60秒松
            print_xbee(
                "!!!!!!!panorama composition finish!!!!! After 1min send!!!")
            time.sleep(60)
            img_string = xbee.image_to_byte(img1)
            xbee.img_trans(img_string)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(panorama composition)-----#####')
        print_xbee('#####-----Error(panorama composition)-----#####\n \n')
