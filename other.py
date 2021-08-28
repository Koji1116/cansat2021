import os
import linecache

def is_dir(path):
    """
    /home/pi/Desktop/Cansat
    以降のディレクトリが存在するかを調べる関数
    """
    rfd = 0
    t_rfd = []
    i = -1
    while rfd > 0:
        rfd = path.rfind('/', 17, t_rfd[i])
        print(rfd)
        t_rfd.append(rfd)
        i += 1
    return t_rfd


def log(path, *data):
    """
    制御ログのための関数
    前半はgit管理でログ作成用
    後半はgit管理外でログ作成用(git操作間違えてもログを残すため)
    """
    with open(path, "a") as f:
        for i in range(len(data)):
            if isinstance(data[i], list):
                for j in range(len(data[i])):
                    f.write(str(data[i][j]) + "\t")
            else:
                f.write(str(data[i]) + "\t")
        f.write("\n")

    # for log outside of git management
    rfd = path.rfind('/')
    path_backup = '/home/pi/Desktop/log' + path[rfd:]
    with open(path_backup, "a") as f:
        for i in range(len(data)):
            if isinstance(data[i], list):
                for j in range(len(data[i])):
                    f.write(str(data[i][j]) + "\t")
            else:
                f.write(str(data[i]) + "\t")
        f.write("\n")


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


def phase(path):
    """
    フェーズ番号を取得するための関数
    フェーズを記録するファイルの一番最後のフェーズ番号を取得する
    """
    num_lines = sum(1 for line in open(path))
    lastLine = linecache.getline(path, num_lines)
    if not lastLine:
        return 0
    phase = lastLine[0]
    linecache.clearcache()
    return int(phase)



if __name__ == "__main__":
    print(is_dir('/home/pi/Desktop/Cansat2021ver/log/phaseLog'))
