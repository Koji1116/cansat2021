import picamera
import time
import traceback
import os


def picture(path, width=320, height=240):
    def filename(f, ext):
        i = 0
        while 1:
            num = ""
            if len(str(i)) <= 4:
                for j in range(4 - len(str(i))):
                    num = num + "0"
                num = num + str(i)
            else:
                num = str(i)
            if not (os.path.exists(f + num + "." + ext)):
                break
            i = i + 1
        f = f + num + "." + ext
        return f

    try:
        with picamera.PiCamera() as camera:
            camera.rotation = 270
            # 取得した画像の回転
            camera.resolution = (width, height)
            # 取得する画像の解像度を設定→どのような基準で設定するのか
            # 使用するカメラの解像度は静止画解像度で3280×2464
            filepath = filename(path, "jpg")
            # 指定したパスを持つファイルを作成

            camera.capture(filepath)
    # そのファイルに取得した画像を入れる
    except picamera.exc.PiCameraMMALError:
        filepath = "Null"
        # パスが切れているときはNULL
        time.sleep(0.8)
    except:
        print(traceback.format_exc())
        time.sleep(0.1)
        filepath = "Null"
    # そのほかのエラーの時はNULL
    return filepath


if __name__ == "__main__":
    try:
        photoName = picture("photo/photo", 320, 240)
    except KeyboardInterrupt:
        print('stop')
    except:
        print(traceback.format_exc())
