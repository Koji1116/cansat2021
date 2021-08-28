import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/other')

import Xbee
import Capture
import other


try:
    Xbee.on()
    while 1:
        received_str = Xbee.receive_str()

        # received_str = ''
        # while received_str == '':
        #     received_str = Xbee.receive_str()

        if received_str == 'a':
            Capture.Capture('photostorage/remote_photo')
            print('photoed')

except KeyboardInterrupt:
    print('interruppted')
    Xbee.off()