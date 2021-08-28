import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/camera')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/motor')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/illuminance')
import time
import capture
import ParaDetection
import Motor
import TSL2561
import cv2


def ParaJudge():
	t1 = time.time()
	t2 = t1
	while(t2 - t1 <= 60):
		lux=TSL2561.readLux()
		print("lux1: "+str(lux[0]))

		if lux[0]<100:
			time.sleep(5)
			t2 = time.time()
		else:
			break

def ParaAvoidance():
	n = 0
	#gps.openGPS()
	#GPS_init = gps.readGPS()
	#gps.closeGPS()

	#GPS_now = GPS_init
	dist = 0
	try:
		while dist <= 0.020 :
			capture.Capture(n)
			img = cv2.imread('photo/photo' + n + '.jpg')
			flug = ParaDetection.paradetection(img)
			if flug == 0:
				Motor.motor(50,50,2)
				#GPS_now = gps.readGPS()
				#dist = Cal_rho(GPS_now[2], GPS_now[1], GPS_init[2], GPS_init[1])
				Motor.motor_stop()
				dist += 0.02

			else:
				Motor.motor(-30,30,1)
				Motor.motor_stop()

	except KeyboardInterrupt:
		Motor.motor_stop()
	
	#gps.closeGPS()

if __name__ == '__main__':
	print("ParaJudge start")
	ParaJudge()
	print("ParaAvoidance start")
	ParaAvoidance()