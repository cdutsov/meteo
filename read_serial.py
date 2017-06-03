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
    sentence = ''
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        while 'RMC' not in sentence:
            sentence = ser.readline().split('$', 1)
            if len(sentence) == 2:
                sentence = sentence[1]
            else:
                sentence = ''

            print sentence

        msg = pynmea2.parse(sentence)
        print msg
        return msg


latlon = get_gps()
print latlon
# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
