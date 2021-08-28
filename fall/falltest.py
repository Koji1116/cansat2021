import time
import datetime
import pigpio
import sys

from sensor.envirionmental import bme280
from sensor.communication import xbee
from sensor.gps import gps
from other.escape import escape
from other import other
from detection import release
from detection import land


pi = pigpio.pi()

# variable for timeout
t_setup = 60
t_out_release = 60
t_out_release_safe = 1000
t_out_land = 40


# variable for releasejudge
thd_press_release = 0.3
press_count_release = 0
press_judge_release = 0
t_delta_release = 1.3  # エレベータ:3    パラシュート落下:0.9 ?

# variable for landjudgment
thd_press_land = 0.15
press_count_land = 0
press_judge_land = 0

# variable used for ParaDetection
LuxThd = 100
imgpath_para = "/home/pi/Desktop/Cansat2021ver/photostorage/paradetection"

# path for save
phaseLog = "/home/pi/Desktop/Cansat2021ver/log/phaseLog"
waitingLog = "/home/pi/Desktop/Cansat2021ver/log/waitingLog.txt"
releaseLog = "/home/pi/Desktop/Cansat2021ver/log/releaseLog.txt"
landingLog = "/home/pi/Desktop/Cansat2021ver/log/landingLog.txt"
meltingLog = "/home/pi/Desktop/Cansat2021ver/log/meltingLog.txt"
paraAvoidanceLog = "/home/pi/Desktop/Cansat2021ver/log/paraAvoidanceLog.txt"
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/panorama_src'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/panorama_dst'


def setup():
    global phaseChk
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    gps.openGPS()


def close():
    gps.closeGPS()
    xbee.off()


if __name__ == '__main__':
    xbee.on()
    while 1:
        xbee.str_trans('standby\t')
        if xbee.str_receive() == 's':
            xbee.str_trans('\n')
            xbee.str_trans('#####-----Program start-----#####\n \n')
            break

    try:
        t_start = time.time()
        # ------------------- Setup Phase --------------------- #
        xbee.str_trans('#####-----Setup Phase start-----#####')
        other.saveLog(phaseLog, "1", "Setup phase", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        setup()
        xbee.str_trans('#####-----Setup Phase ended-----##### \n \n')

        # ------------------- Waiting Phase --------------------- #
        xbee.str_trans('#####-----Waiting Phase start-----#####')
        other.saveLog(phaseLog, "2", "Waiting Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        # if phaseChk == 2:
        #     t_wait_start = time.time()
        #     while time.time() - t_wait_start <= t_setup:
        #         other.saveLog(waitingLog, time.time() - t_start, gps.readGPS(), bme280.bme280_read(), TSL2572.read())
        #         print('Waiting')
        #         xbee.str_trans('Sleep')
        #         time.sleep(1)
        xbee.str_trans('#####-----Waiting Phase ended-----##### \n \n')

        # ------------------- Release Phase ------------------- #
        xbee.str_trans('#####-----Release Phase start-----#####')
        other.saveLog(phaseLog, "3", "Release Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
            t_release_start = time.time()
            i = 1
            try:
                while time.time() - t_release_start <= t_out_release:
                    xbee.str_trans(f'loop_release\t {i}')
                    press_count_release, press_judge_release = release.pressdetect_release(thd_press_release,
                                                                                           t_delta_release)
                    xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                    other.saveLog(releaseLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS,
                                  bme280.bme280_read(), press_count_release, press_judge_release)
                    if press_judge_release == 1:
                        xbee.str_trans('Release\n \n')
                        break
                    else:
                        xbee.str_trans('Not Release\n \n')
                    i += 1
                else:
                    # 落下試験用の安全対策（落下しないときにxbeeでプログラム終了)
                    while time.time() - t_release_start <= t_out_release_safe:
                        xbee.str_trans('continue? y/n \t')
                        if xbee.str_receive() == 'y':
                            break
                        elif xbee.str_receive() == 'n':
                            xbee.str_trans('Interrupted for safety')
                            exit()
                    xbee.str_trans('##--release timeout--##')
            except KeyboardInterrupt:
                print('interrupted')
            xbee.str_trans("######-----Released-----##### \n \n")

        # ------------------- Landing Phase ------------------- #
        xbee.str_trans('#####-----Landing Phase start-----#####')
        other.saveLog(phaseLog, "4", "Landing Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase\t{phaseChk}')
        if phaseChk == 4:
            xbee.str_trans(f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                xbee.str_trans(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(thd_press_land)
                xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                i += 1
            else:
                xbee.str_trans('Landed Timeout')
            other.saveLog(landingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(),
                          bme280.bme280_read(), 'Land judge finished')
            xbee.str_trans('######-----Landed-----######\n \n')

        # ------------------- Melting Phase ------------------- #
        xbee.str_trans('#####-----Melting phase start#####')
        other.saveLog(phaseLog, '5', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 5:
            other.saveLog(meltingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(), "Melting Start")
            #安全対策(2021では他の階の手すりにパラシュートが引っかかってそこから落下しました)
            while 1:
                xbee.str_trans('continue? y/n \t')
                if xbee.str_receive() == 'y':
                    escape.escape()
                    break
                elif xbee.str_receive() == 'n':
                    xbee.str_trans('Interrupted for safety')
                    exit()
            time.sleep(3)
            other.saveLog(meltingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(), "Melting Finished")
        xbee.str_trans('########-----Melted-----#######\n \n')
        # ------------------- ParaAvoidance Phase ------------------- #
        # xbee.str_trans("#####-----ParaAvo phase start-----#####")
        # if stuck.ue_jug():
        #     pass
        # else:
        #     motor.move(12,12,0.2)


        # other.saveLog(phaseLog, "6", "ParaAvoidance Phase Started", time.time() - t_start, datetime.datetime.now())
        # phaseChk = other.phaseCheck(phaseLog)
        # xbee.str_trans(f'Phase:\t{phaseChk}')
        # if phaseChk == 6:
        #     t_ParaAvoidance_start = time.time()
        #     t_parajudge = time.time()
        #     other.saveLog(paraAvoidanceLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(),
        #                   'ParaAvo Start')
        #     # while time.time() - t_parajudge < 60:
        #     #     Luxflug, Lux = paradetection.ParaJudge(LuxThd)
        #     #     xbee.str_trans(f'Luxflug: {Luxflug}\t lux: {Lux}\n')
        #     #     if Luxflug == 1:
        #     #         xbee.str_trans(f'rover is not covered with parachute. Lux: {Lux}\n')
        #     #         break
        #     #     else:
        #     #         xbee.str_trans(f'rover is covered with parachute! Lux: {Lux}\n')
        #     #         time.sleep(1)
        #     xbee.str_trans(f'Prachute avoidance Started \t{time.time() - t_start}\n')
        #     # --- first parachute detection ---#
        #     count_paraavo = 0
        #     while count_paraavo < 1:
        #         flug, area, gap, photoname = paradetection.ParaDetection(
        #             "photostorage/para", 320, 240, 200, 10, 120, 1)
        #         xbee.str_trans(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
        #         other.saveLog(paraAvoidanceLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS, flug, area,
        #                       gap, photoname)
        #         paraavoidance.Parachute_Avoidance(flug, gap)
        #         if flug == -1 or flug == 0:
        #             count_paraavo += 1
        #     xbee.str_trans('#####-----paraavoided-----#####\n \n')

        # # ------------------- Panorama Shooting Phase ------------------- #
        # # mag.bmc050_setup()
        # # xbee.str_trans('#####-----Panorama-----#####\n')
        # # other.saveLog(phaseLog, '7', 'Panorama Shooting phase', time.time() - t_start)
        # # phaseChk = other.phaseCheck(phaseLog)
        # # xbee.str_trans(f'Phase: {phaseChk}\n')
        # # if phaseChk <= 7:
        # #     t_PanoramaShooting_start = time.time()
        # #     print(f'Panorama Shooting Phase Started {time.time() - t_start}')
        # #     magdata = calibration.magdata_matrix()
        # #     magx_off, magy_off = calibration.calculate_offset(magdata)
        # #     panorama.shooting(20, -20, 0.2, magx_off, magy_off, path_src_panorama)
        # #     panorama.composition(srcdir=path_src_panorama, dstdir=path_dst_panoraam)
        xbee.str_trans('########--Progam Finished--##########')
        close()
    except KeyboardInterrupt:
        close()
        print("Keyboard Interrupt")
    except Exception as e:
        xbee.str_trans("error")
        close()
        other.saveLog("/home/pi/Desktop/Cansat2021ver/log/errorLog.txt", t_start - time.time(), "Error")
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
