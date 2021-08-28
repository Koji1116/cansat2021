#---↓設定（ここら辺は難しいので無視でも大丈夫です。）----
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/sensor/motor')
from gpiozero import Motor
import time
Rpin1, Rpin2 = 5, 6
Lpin1, Lpin2 = 10, 9
#---↓右側motorを動かすための設定
motor_r = Motor(Rpin1, Rpin2)
#---↓左側motorを動かすための設定
motor_l = Motor(Lpin1, Lpin2)





#例えば、ローバーを１秒間、出力(0~1で指定)0.2で前進させたいときは次のようにコードを書く。
# motor_r.forward(0.2)  #右のモータ動かす指令
# motor_l.forward(0.2)  #左のモータ動かす指令
# time.sleep(1)         #1秒間待つ
# motor_r.stop()        #右のモータ止める指令
# motor_l.stop()        #左のモータ止める指令


#--------課題----------#
#問題：'w'が入力されたら１秒間前進、'a'が入力されたら１秒間斜め左方向に前進、'd'が入力されたら1秒間斜め右方向前進
#      というコードを下に書いてください。
#ヒント1：入力に関してはinput関数を使う(参考url:https://qiita.com/naoya_ok/items/f33a6ab2ff77154a7121)
#ヒント2：場合分けはif文使う(参考url:https://note.nkmk.me/python-if-elif-else/) 
while 1:

    print("文字を入力")
    n=input()
    if n=="w":
        motor_r.forward(0.2)  #右のモータ動かす指令
        motor_l.forward(0.2)  #左のモータ動かす指令
        time.sleep(1)         #1秒間待つ
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令
    elif n=="a":
        motor_r.forward(0.1)  #右のモータ動かす指令
        motor_l.backward(0.1)  #左のモータ動かす指令
        time.sleep(0.5)         #1秒間待つ
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令
        motor_r.forward(0.2)  #右のモータ動かす指令
        motor_l.forward(0.2)  #左のモータ動かす指令
        time.sleep(1)         #1秒間待つ
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令
    elif n=="d":
        motor_r.backward(0.1)  #右のモータ動かす指令
        motor_l.forward(0.1)  #左のモータ動かす指令
        time.sleep(0.5)         #1秒間待つ
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令
        motor_r.forward(0.2)  #右のモータ動かす指令
        motor_l.forward(0.2)  #左のモータ動かす指令
        time.sleep(1)         #1秒間待つ
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令
    else:
        motor_r.stop()        #右のモータ止める指令
        motor_l.stop()        #左のモータ止める指令