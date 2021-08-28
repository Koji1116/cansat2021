import serial

port = serial.Serial(
        port = "/dev/ttyAMA0",
		baudrate = 57600,
		parity = serial.PARITY_NONE,
		stopbits = serial.STOPBITS_ONE,
		bytesize = serial.EIGHTBITS,
		timeout = 5
	    )

#現在使用中のチャンネルを別のチャンネルに変更する関数
def Change_Channel():
    print('Status  : Start ATmode')
    Enter_ATmode = '+++'
    Enter_ATmode = Enter_ATmode.encode()
    commands = [Enter_ATmode]

    for cmd in commands:
        port.write(cmd)
        response = port.read(2)
        response = response.decode()

        if response == 'OK' :
            print('Status  : Enter ATmode')
            CH = str(input('変更後のチャンネルは？'))
            change_CH = 'ATCH' + CH + '\r'
            change_CH = change_CH.encode()
            commands = [change_CH]
            for cmd in commands:
                port.write(cmd)
                print('Status  : Change Channel')
        else:
                print('Status  : Failed')
                break
    port.close()
    
Change_Channel()
