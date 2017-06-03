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
        no_spd = True
        no_alt = True
        while no_alt or no_spd:
            sentence = ser.readline().split('$', 1)
            if len(sentence) == 2:
                sentence = sentence[1]
            else:
                sentence = ''
            print sentence
            if 'RMC' in sentence:
                msg = pynmea2.parse(sentence)
                lat = msg.latitude
                lon = msg.longitude
                no_spd = False
                # speed = msg.speed
            elif 'GGA' in sentence:
                msg = pynmea2.parse(sentence)
                alt = msg.altitude
                no_alt = True
        return lon, lat, alt, speed

# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
