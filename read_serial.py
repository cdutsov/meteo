import serial
import time
import signal
import sys

# ser = serial.Serial(
#     port='/dev/ttyS0',
#     baudrate=9600,
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS,
#     timeout=0)


def signal_handler(signal, frame):
    ser.close()
    print('Serial closed!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# print("connected to: " + ser.portstr)

# this will store the line
# seq = []
# count = 1

while True:
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        line = ser.readline()
        print line