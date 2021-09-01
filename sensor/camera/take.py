import picamera
import time
import traceback
import os


def picture(path, width=320, height=240):
    """写真を取るための関数"""
    def dir(path):
        """
        /dir/dir/dir/fileの時にfileの前にディレクトリが存在するか調べる関数
        引数は/dir/dir/dir/fileの形のパス
        """
        fd = path.rfind('/')
        dir = path[:fd]

        is_dir = os.path.isdir(dir)
        return is_dir
    def make_dir(path):
        """
        dir関数で調べた結果ディレクトリが存在しない場合はそのディレクトリを作成する
        """
        if not dir(path):
            fd = path.rfind('/')
            directory = path[:fd]
            os.mkdir(directory)
            print('******Directory is maked******')
        else:
            print('**Directory is exist**')
    def filename(f, ext):
        """
        ファイル名に番号をつけるための関数
        引数f:つけたいファイル名
        引数ext:ファイルの拡張子
        戻り値f:ファイル名+0000.拡張子
        戻り値の番号は増えていく
        """
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
        make_dir(path)
        with picamera.PiCamera() as camera:
            camera.rotation = 270
            # 取得した画像の回転
            camera.resolution = (width, height)
            # 取得する画像の解像度を設定→どのような基準で設定するのか
            # 使用するカメラの解像度は静止画解像度で3280×2464
            filepath = filename(path, 'jpg')
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


if __name__ == '__main__':
    try:
        photoName = picture('photo/photo', 320, 240)
    except KeyboardInterrupt:
        print('stop')
    except:
        print(traceback.format_exc())
