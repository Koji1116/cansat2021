import time
import picamera

with picamera.PiCamera() as camera:
	camera.resolution = (1024, 768)
	camera.start_preview()
	time.sleep(2)
	camera.start_recording('video_test.h264')
	camera.wait_recording(5)

	camera.stop_recording()
	camera.stop_preview()