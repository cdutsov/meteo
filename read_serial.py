import serial
import time
import signal
import sys

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)


def signal_handler(signal, frame):
    ser.close()
    print('Serial closed!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("connected to: " + ser.portstr)

# this will store the line
seq = []
count = 1

with serial.Serial('/dev/ttyS0', 19200, timeout=1) as ser:
    x = ser.read()  # read one byte
    line = ser.readline()  # read a '\n' terminated line
    print line
# while True:
#    for mee in ser.read():
#        seq.append(chr(mee))
#        joined_seq = ''.join(str(v) for v in seq)

#        if chr(mee) == '\n':
#            print("Line " + str(count) + ': ' + joined_seq)
#            seq = []
#            count += 1
#            break
ser.close()
