from gpiozero import Motor
import time

from parts.detection import stuck


def setup():
    global motor_r, motor_l
    Rpin1, Rpin2 = 5, 6
    Lpin1, Lpin2 = 10, 9
    motor_r = Motor(Rpin1, Rpin2)
    motor_l = Motor(Lpin1, Lpin2)

def motor_continue(strength_l, strength_r):
    strength_l = strength_l/100
    strength_r = strength_r/100
    if strength_r >= 0 and strength_l >= 0:
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r.forward(abs(strength_r))
        motor_l.backward(abs(strength_l))
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r.backward(abs(strength_r))
        motor_l.forward(abs(strength_l))



def motor_stop(x=1):
    '''motor_move()とセットで使用'''
    motor_r.stop()
    motor_l.stop()
    time.sleep(x)


# def motor_move_acc(strength_l, strength_r, t_moving):
#     '''
#     引数は左のmotorの強さ、右のmotorの強さ、走る時間。
#     strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
#     必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    
#     '''
#     strength_r /= 100
#     strength_l /= 100
#     acc.bmc050_setup()
#     Rpin1 = 5
#     Rpin2 = 6
#     Lpin1 = 10
#     Lpin2 = 9
#     # 前進するときのみスタック判定
#     if strength_r >= 0 and strength_l >= 0:
#         motor_r = motor(Rpin1, Rpin2)
#         motor_l = motor(Lpin1, Lpin2)
#         motor_r.forward(strength_r)
#         motor_l.forward(strength_l)
#         time.sleep(0.2)
#         print(acc.acc_dataRead())
        
#     # 後進
#     elif strength_r < 0 and strength_l < 0:
#         motor_r = motor(Rpin1, Rpin2)
#         motor_l = motor(Lpin1, Lpin2)
#         motor_r.backward(abs(strength_r))
#         motor_l.backward(abs(strength_l))
#         time.sleep(0.2)
#         print(acc.acc_dataRead())
        
#     # 右回転
#     elif strength_r >= 0 and strength_l < 0:
#         motor_r = motor(Rpin1, Rpin2)
#         motor_l = motor(Lpin1, Lpin2)
#         motor_r.forward(abs(strength_r))
#         motor_l.backward(abs(strength_l))
#         time.sleep(0.2)
#         print(acc.acc_dataRead())
        

#     # 左回転
#     elif strength_r < 0 and strength_l >= 0:
#         motor_r = motor(Rpin1, Rpin2)
#         motor_l = motor(Lpin1, Lpin2)
#         motor_r.backward(abs(strength_r))
#         motor_l.forward(abs(strength_l))
        
#         print(acc.acc_dataRead())
        



def motor_move(strength_l, strength_r, t_moving):
    '''
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    '''
    strength_l = strength_l/100
    strength_r = strength_r/100
    # 前進するときのみスタック判定
    if strength_r >= 0 and strength_l >= 0:
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
        time.sleep(t_moving)
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(t_moving)
    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r.forward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(t_moving)
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r.backward(abs(strength_r))
        motor_l.forward(abs(strength_l))
        time.sleep(t_moving)

# def move_acc(strength_l, strength_r, t_moving, x=0.1):
#     """
#     急停止回避を組み込み 7/23 takayama
#     """
#     strength_r /= 100
#     strength_l /= 100
#     motor_move_acc(strength_l, strength_r, t_moving)
#     t_stop = time.time()
#     if abs(strength_l) == abs(strength_r) and strength_l * strength_r < 0:
#         motor_stop(x)
#     else:
#         #before
#         # while time.time() - t_stop <= 1:
#         #     coefficient_power = abs(1 - (time.time() - t_stop))
#         #     motor_move(strength_l*coefficient_power, strength_r*coefficient_power, 0.1)


#         #更新(2021-07-24)
#         for i in range(10):
#             coefficient_power = 10 - i
#             coefficient_power /= 10
#             motor_move(strength_l * coefficient_power, strength_r * coefficient_power, 0.1)
#             if i == 9:
#                 motor_stop(x)


def deceleration(strength_l, strength_r):
    for i in range(10):
        coefficient_power = 10 - i
        coefficient_power /= 10
        motor_move(strength_l * coefficient_power, strength_r * coefficient_power, 0.1)
        if i == 9:
            motor_stop(0.1)

def move(strength_l, strength_r, t_moving, ue = False):
    """
    急停止回避を組み込み 7/23 takayama
    """
    if ue:
        stuck.ue_jug()
    motor_move(strength_l, strength_r, t_moving)
    if abs(strength_l) == abs(strength_r) and strength_l * strength_r < 0:
        motor_stop(0.1)
    else:
        deceleration(strength_l, strength_r)



if __name__ == '__main__':
    setup()
    while 1:
        command = input('操作\t')
        if command == 'a':
            move(40, 80, 2)
        elif command == 'w':
            move(80, 80, 2)
        elif command == 'd':
            move(80, 40, 2)
        elif command == 's':
            move(-50, -50, 2)
        elif command == 'manual':
            l = float(input('左の出力は？'))
            r = float(input('右の出力は？'))
            t = float(input('移動時間は？'))
            time.sleep(0.8)
            move(l, r, t)
        else:
            print('もう一度入力してください')