import serial

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

print("connected to: " + ser.portstr)
count = 1

while True:
    for line in ser:
            print line
            # print str(count) + str(': ') + line
            count = count + 1

ser.close()
