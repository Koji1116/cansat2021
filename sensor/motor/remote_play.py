import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')

import Xbee
import motor
import time

try:
    Xbee.on()
    motor.setup()
    while 1:
        Xbee.str_trans('操作\t')
        command = Xbee.str_receive()
        if command == 'a':
            motor.move(40, 80, 2)
        elif command == 'w':
            motor.move(80, 80, 2)
        elif command == 'd':
            motor.move(80, 40, 2)
        elif command == 's':
            motor.move(-50, -50, 2)
        else:
            Xbee.str_trans('もう一度入力してください')
        # received_str = ''
        # while received_str == '':
        #     received_str = Xbee.receive_str()

except KeyboardInterrupt:
    print('interruppted')
    Xbee.off()
