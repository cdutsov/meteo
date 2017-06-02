import serial
import pynmea2


def get_dust_particles():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        sentence = ser.readline()
        dat = 0.
        try:
            dat = float(sentence.rsplit(',')[1])
        except:
            dat = False
        return dat

def get_gps():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        sentence = ser.readline().split('$', 1)
        if len(sentence) > 1:
            print pynmea2.parse(sentence[1])

# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
