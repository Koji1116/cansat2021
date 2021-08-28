import math
import time

from parts.calibration import calibration
from parts.sensor.axis import mag
from parts.sensor.motor import motor


def angle(magx, magy, magx_off=0, magy_off=0):
    θ = math.degrees(math.atan((magy - magy_off) / (magx - magx_off)))

    if magx - magx_off > 0 and magy - magy_off > 0:  # First quadrant
        pass  # 0 <= θ <= 90
    elif magx - magx_off < 0 and magy - magy_off > 0:  # Second quadrant
        θ = 180 + θ  # 90 <= θ <= 180
    elif magx - magx_off < 0 and magy - magy_off < 0:  # Third quadrant
        θ = θ + 180  # 180 <= θ <= 270
    elif magx - magx_off > 0 and magy - magy_off < 0:  # Fourth quadrant
        θ = 360 + θ  # 270 <= θ <= 360

    θ += 90
    if 360 <= θ <= 450:
        θ -= 360

    return θ


if __name__ == '__main__':
    motor.setup()
    mag.bmc050_setup()
    try:
        r = float(input('右の出力は？\t'))
        l = float(input('左の出力は\t'))
        t = float(input('何秒間回転する\t'))
        n = int(input('整数値入力適当な値でよい\t'))
        magdata_offset = calibration.magdata_matrix(l, r, t, n)
        magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = calibration.calculate_offset(magdata_offset)
        time.sleep(0.1)
        while True:
            magdata = mag.mag_dataread()
            mag_x = magdata[0]
            mag_y = magdata[1]
            θ = angle(mag_x, mag_y, magx_off, magy_off)
            #print(mag_x,mag_y)
            print(θ)
            # print(theta )
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('end')

