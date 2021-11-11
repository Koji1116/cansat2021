import sys
sys.path.append('../../')
import io
from PIL import Image
import other
import serial
import pigpio

pi = pigpio.pi()

def image_to_byte(img1):
    img = Image.open(img1)
    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        ImgTobyte = output.getvalue()
        return ImgTobyte


def img_trans(string):
    port = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )
    port.write(string)
    port.close()


def str_trans(string):
    string = str(string)
    ser = serial. Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=5
    )
    string = string + '\n'
    moji = string.encode()
    commands = [moji]
    for cmd in commands:
        ser.write(cmd)
    ser.flush()
    ser.close()


def str_receive():
    ser = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )
    received = ser.read()
    received_str = received.decode()
    return received_str


def on():
    pi.write(12, 1)


def off():
    pi.write(12, 0)


if __name__ == '__main__':
    on()
    other.print_xbee("abc")
    
    # a = input('何送る？')
    # img1 = "/home/pi/Desktop/cansat2021ver/dst_panorama/"+ a +".jpg"
    # img_string = image_to_byte(img1)
    # img_trans(img_string)
