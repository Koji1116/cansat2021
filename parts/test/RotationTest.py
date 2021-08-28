import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')


import motor
import BMC050
from parts import calibration
import Xbee

def rotation(magx_off, magy_off, count=1):
    """
    回転テスト用(パノラマ撮影もこれからスタート？)
    引数は磁気のオフセット、countは回転する回数
    takayama
    """
    for _ in range(count):
        magdata = BMC050.mag_dataread()
        magx = magdata[0]
        magy = magdata[1]
        preθ = calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        sumθ = 0
        deltaθ = 0
        Xbee.str_trans('whileスタート {0}'.format(preθ))

        while sumθ <= 360:
            motor.motor_move(-1, 1, 1) #調整するところ？
            magdata = BMC050.mag_dataread()
            magx = magdata[0]
            magy = magdata[1]
            latestθ = calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
            if preθ >= 300 and latestθ <= 100:
                latestθ += 360
            deltaθ = preθ - latestθ
            sumθ += deltaθ
            if latestθ >= 360:
                latestθ -= 360
            preθ = latestθ
            Xbee.str_trans('sumθ:', sumθ, ' preθ:', preθ, ' deltaθ:', deltaθ)


if __name__ == "__main__":
    try:
        motor.setup()
        BMC050.bmc050_setup()
        magdata = calibration.magdata_matrix()  #magdata_matrix()内を変更する必要あり2021/07/04
        _, _, _, magx_off, magy_off, _ = calibration.calculate_offset(magdata)
        rotation(magx_off, magy_off)
    except:
        print('error')