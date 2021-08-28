import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/sensor/axis')
# sys.path.append('/home/pi/desktop/Cansat2021ver/sensor/motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/sensor/communication')
sys.path.append('/home/pi/desktop/Cansat2021ver/sensor/motor')
import time
from gpiozero import Motor


# ピン番号は仮
Rpin1 = 5
Rpin2 = 6

Lpin1 = 9
Lpin2 = 10

def motor_stop(x=1):
    '''motor_move()とセットで使用'''
    Rpin1 = 10
    Rpin2 = 9
    Lpin1 = 6
    Lpin2 = 5
    motor_r = Motor(Rpin1, Rpin2)
    motor_l = Motor(Lpin1, Lpin2)
    motor_r.stop()
    motor_l.stop()
    time.sleep(x)


def motor_move(strength_l, strength_r, time_wait):
    '''
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    '''
    Rpin1 = 10
    Rpin2 = 9
    Lpin1 = 6
    Lpin2 = 5
    # 前進するときのみスタック判定
    if strength_r >= 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
        time.sleep(time_wait)
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(time_wait)
    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forkward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(time_wait)
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forkward(abs(strength_l))
        time.sleep(time_wait)


def motor(strength_l, strength_r, time_wait, x=1):
    motor_move(strength_l, strength_r, time_wait)
    motor_stop(x)

if __name__ == '__main__':
    while 1:
        a =input('入力しろ')
        if a =='a':
            motor(0.5,0.8,2.0)
        elif a =='w':
            motor(0.8,0.8,2)
        elif a =='d':
            motor(0.8,0.5,2)
        elif a =='s':
            motor(-0.5,-0.5,2)
        elif a =='f':
             motor(-0.5,0.5,2)
        else:
            pass
