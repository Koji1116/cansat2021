import io
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import serial

ser = serial.Serial(
       port = "COM3", 
       baudrate= 57600, 
       parity = serial.PARITY_NONE,
       stopbits = serial.STOPBITS_ONE,
       bytesize = serial.EIGHTBITS,
       timeout = 10
       )


def bytes_receive():
    img_bytes = ser.readlines()
    img_bytes1 = b"".join(img_bytes) #リスト　→　文字列  
    ser.close()
    print("End")
    return img_bytes1
    
def convert_img(img_bytes):
    ByteToImg = Image.open(io.BytesIO(img_bytes))
    ByteToImg.save('decoded_img_01.jpg')
    
if __name__ == '__main__':
    while True:
        Check＿transfer_1 = ser.readline().strip().decode('utf-8')
        if Check＿transfer_1 == 'Ready?':
            Check＿transfer_2 = ser.write(b'Ready!')
            break

    img_bytes = bytes_receive()
    print('Receive Complete')
    img = convert_img(img_bytes)
    print('Convert Complete')
    print('All Complete')