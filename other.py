import os
import linecache

from sensor.communication import xbee


def print_xbee(word, com=True):
    """
    printによる出力とxbeeによる送信を一緒に行うための関数
    """
    print(word)
    if com:
        xbee.str_trans(word)


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
        dir = path[:fd]
        os.mkdir(dir)
        print('******Directory is maked******')
    else:
        print('**Directory is exist')


def log(path, *data):
    """
    制御ログのための関数
    前半はgit管理でログ作成用
    後半はgit管理外でログ作成用(git操作間違えてもログを残すため)
    """
    with open(path, 'a') as f:
        for i in range(len(data)):
            if isinstance(data[i], list):
                for j in range(len(data[i])):
                    f.write(str(data[i][j]) + "\t")
            else:
                f.write(str(data[i]) + "\t")
        f.write('\n')

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
        num = ''
        if len(str(i)) <= 4:
            for j in range(4 - len(str(i))):
                num = num + '0'
            num = num + str(i)
        else:
            num = str(i)
        if not (os.path.exists(f + num + '.' + ext)):
            break
        i = i + 1
    f = f + num + '.' + ext
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
    path = '/home/pi/Desktop/cansat2021/log1/phaseLog'
    print(dir(path))
    make_dir(path)
