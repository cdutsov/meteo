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
# this will store the line
line = []

while True:
    line = ser.readline()
    print line

while True:
    for c in ser.read():
        line.append(c)
        if c == '\n':
            print("Line: " + line)
            line = []
            break

# while True:
#    line = str(ser.readline())
#    print line
#    # print str(count) + str(': ') + line
#    count = count + 1

ser.close()
