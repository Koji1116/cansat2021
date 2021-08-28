import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/gps')

import GPS
import xbee


if __name__ == '__main__':
    try:
        GPS.openGPS()
        xbee.on()
        while 1:
            _, lat, lon, _, _, = GPS.GPSdata_read()
            print(f'lat: {lat} \t lon:{lon}')
            xbee.str_trans(f'lat: {lat} \t lon:{lon}\n \n')
    except KeyboardInterrupt:
        print('Interrupted')
        xbee.str_trans('Interrupted')
        GPS.closeGPS()
        xbee.off()


