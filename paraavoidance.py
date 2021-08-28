# 着地判定後にキャリブレーション前にパラシュート回避を行う
# パラシュート回避エリアは設定せずに、パラシュートが検出されない場合が3回以上(下のプログラムのzで設定)
# のときパラシュート回避を行ったと判定
# そこでキャリブレーションを行い、ローバーをゴール方向に向かせる。
# そのあとにもう一度パラシュート回避を同じ判定方法で行ってGPS走行に移行する。

import traceback

import motor
import paradetection


def parachute_avoidance(flug, goalGAP):
    # --- There is Parachute around rover ---#

    if flug == 1:
        # --- Avoid parachute by back control ---#
        try:
            # goalflug, goalarea, goalGAP, photoname = photorunning.GoalDetection("photostorage/photostorage_paradete/para",320,240,200,10,120)
            if goalGAP >= -100 and goalGAP <= -50:
                motor.move(50, -50, 0.1)
                # motor.move(50, 50, 1)
                # print('# motor.move(50, -50, 0.1)# motor.move(70, 70, 1)')
            if goalGAP >= -50 and goalGAP <= 0:
                motor.move(50, -50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(80, -80, 1)motor.move(70, 70, 1)')
            if goalGAP >= 0 and goalGAP <= 50:
                motor.move(-50, 50, 0.1)
                # motor.move(70, 70, 1)
                # print('motor.move(-50, 50, 0.1)motor.move(70, 70, 1)')
            if goalGAP >= 50 and goalGAP <= 100:
                motor.move(-50, 50, 0.1)
                # motor.move(50, 50, 1)
                # print(' # motor.move(-80, 80, 1)# motor.move(70, 70, 1)')

        except KeyboardInterrupt:
            print("stop")
    if flug == -1 or flug == 0:
        # print('flug')
        motor.move(50, 50, 0.5)


if __name__ == '__main__':
    try:
        motor.setup()
        # print("START: Judge covered by Parachute")
        # TSL2561.tsl2561_setup()
        # t2 = time.time()
        # t1 = t2
        # --- Paracute judge ---#
        # --- timeout is 60s ---#
        # while t2 - t1 < 60:
        # Luxflug = ParaDetection.ParaJudge(10000)
        # print(Luxflug)
        # if Luxflug[0] == 1:
        #	break
        # t1 =time.time()
        # time.sleep(1)
        # print("rover is covered with parachute!")

        print("START: Parachute avoidance")

        flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320, 240,
                                                                  200, 10, 120, 1)
        print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
        print("paradetection phase success")
        count_paraavo = 0
        while count_paraavo < 3:
            flug, area, gap, photoname = paradetection.para_detection("photostorage/photostorage_paradete/para", 320,
                                                                      240, 200, 10, 120, 1)
            print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}')
            parachute_avoidance(flug, gap)
            print(flug)
            if flug == -1 or flug == 0:
                count_paraavo += 1
                print(count_paraavo)

        print("パラシュート回避完了")

    except KeyboardInterrupt:
        print("emergency!")

    except:
        print(traceback.format_exc())
    print("finish!")
