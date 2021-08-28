import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/envirionmental')
# sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')


import time
import serial
import pigpio
import BME280  # envirionmental
# import gps
import traceback

# anyalt = 2
# GAreleasecount = 0
# gpsreleasejudge = 0

anypress = 0.3
pressreleasecount = 0
pressreleasejudge = 0


def pressdetect_release(thd_press_release):
    '''
    気圧による放出判定
    '''
    global presscount_release
    global pressjudge_release
    try:
        pressdata = BME280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress
        if 0.0 in pressdata:
            print("BME280rror!")
            pressjudge_release = 2
            presscount_release = 0
        elif deltP > thd_press_release:
            presscount_release += 1
            if presscount_release > 2:
                pressjudge_release = 1
                print("pressreleasejudge")
        else:
            presscount_release = 0
    except:
        presscount_release = 0
        pressjudge_release = 2
    return presscount_release, pressjudge_release


# def releasejudge(thd_p_release):


if __name__ == "__main__":
    BME280.bme280_setup()
    BME280.bme280_calib_param()

    while True:
        pressreleasecount, pressreleasejudge = pressdetect_release(0.3)
        print(f'count:{pressreleasecount}\tjudge{pressreleasejudge}')
        if pressreleasejudge == 1:
            print('Press')
        else:
            print('unfulfilled')

# def gpsdetect(anyalt):
#     global gpsdata
#     global GAreleasecount
#     gpsreleasejudge = 0
#     try:
#         gpsdata = gps.readGPS()
#         Pregpsalt = gpsdata[3]
#         time.sleep(1)
#         gpsdata = gps.readGPS()
#         Latestgpsalt = gpsdata[3]
#         daltGA = Latestgpsalt - Pregpsalt
#         #print(str(Latestgpsslt)+"   :   "+str(Pregpsalt))
#         if daltGA > anyalt:
#             GAreleasecount += 1
#             if GAreleasecount > 2:
#                 gpsreleasejudge = 1
#                 print("gpsreleasejudge")
#             else:
#                 gpsreleasejudge = 0
#     except:
#         print(traceback.format_exc())
#         GAreleasecount = 0
#         gpsreleasejudge = 2
#     return GAreleasecount, gpsreleasejudge

# if __name__=="__main__":
#
# 	BME280.bme280_setup()
# 	BME280.bme280_calib_param()
# 	gps.openGPS()
#
# 	while True:
# 		_, gpsreleasejudge = gpsdetect(10)
# 		if gpsreleasejudge == 1:
# 			print('gps')
# 		else:
# 			print('gps unfulfilled')
#
# 		_, pressreleasejudge = pressdetect(0.3)
# 		if pressreleasecount == 1:
# 			print('Press')
# 		else:
# 			print('unfulfilled')
