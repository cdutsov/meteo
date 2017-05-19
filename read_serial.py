import serial

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

print("connected to: " + ser.portstr)

# this will store the line
seq = []
count = 1

while True:
    for mee in ser.read():
        seq.append(chr(mee))
        joined_seq = ''.join(str(v) for v in seq)

        if chr(mee) == '\n':
            print("Line " + str(count) + ': ' + joined_seq)
            seq = []
            count += 1
            break

ser.close()
