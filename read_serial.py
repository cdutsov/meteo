import datetime
import serial
import pynmea2


def get_dust_particles():
    try:
        with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
            sentence = ser.readline()
            return int(sentence) * 11 * 3.3 / 4096.0 * 172 - 0.01
    except:
        return 0


def get_gps():
    sentence = ''
    time = datetime.time(00, 00, 00)
    lat, lon, alt, speed = 0, 0, 0, 0
    gps_dat = {}
    # try:
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        no_spd = True
        no_alt = True
        while no_alt or no_spd:
            sentence = ser.readline().split('$', 1)
            if len(sentence) == 2:
                sentence = sentence[1]
            else:
                sentence = ''
            if 'RMC' in sentence:
                msg = pynmea2.parse(sentence)
                gps_dat["latitude"] = msg.latitude
                gps_dat["longitude"] = msg.longitude
                gps_dat["timestamp"] = msg.timestamp
                no_spd = False
                gps_dat["speed"] = msg.spd_over_grnd*0.5144
            elif 'GGA' in sentence:
                msg = pynmea2.parse(sentence)
                gps_dat["altitude"] = msg.altitude
                no_alt = False
        return gps_dat
    # except:
    #     return None

# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
