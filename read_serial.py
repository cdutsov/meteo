import serial
import pynmea2


def get_dust_particles():
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
        sentence = ser.readline()
        return int(sentence) * 11 * 3.3 / 4096.0 * 172 - 0.01


def get_gps():
    sentence = ''
    lat, lon, alt, speed = 0, 0, 0, 0
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        while 'RMC' not in sentence:
            sentence = ser.readline().split('$', 1)
            if len(sentence) == 2:
                sentence = sentence[1]
            else:
                sentence = ''
            print sentence
            msg = pynmea2.parse(sentence)
            lat = msg.latitude
            lon = msg.longitude
            # speed = msg.speed
        while 'GGA' not in sentence:
            sentence = ser.readline().split('$', 1)
            if len(sentence) == 2:
                sentence = sentence[1]
            else:
                sentence = ''
            msg = pynmea2.parse(sentence)
            alt = msg.altitude
        return lon, lat, alt, speed

# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
