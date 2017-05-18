import serial

ser = serial.Serial(
    port='COM5',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

print("connected to: " + ser.portstr)
count = 1

while True:
    for line in ser.readline():
        print(str(count) + str(': ') + chr(line))
        count = count + 1

ser.close()
