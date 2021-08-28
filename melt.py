import time
import pigpio

pi = pigpio.pi()

meltPin = 17

def down(t_melt = 3.5):
	pi.write(meltPin, 0)
	time.sleep(1)
	pi.write(meltPin, 1)
	time.sleep(t_melt)
	pi.write(meltPin, 0)
	time.sleep(1)

if __name__ == "__main__":
	try:
		down()
	except:
		pi.write(meltPin, 0)

