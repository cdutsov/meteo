import datetime
import threading

import serial
import pynmea2


def get_dust_particles():
    try:
        with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
            sentence = ser.readline()
            return int(sentence) * 11 * 3.3 / 4096.0 * 172 - 0.01
    except:
        return 0


def get_gps(ser, gps_dat):
    while True:
        no_spd = True
        no_alt = True
        data = {}
        while no_alt or no_spd:
            sentence = ser.readline().split('$')
            if len(sentence) >= 2:
                sentence = sentence[1]
            else:
                sentence = ''
            if 'RMC' in sentence:
                msg = pynmea2.parse(sentence)
                data["latitude"] = msg.latitude
                data["longitude"] = msg.longitude
                data["timestamp"] = msg.timestamp
                no_spd = False
                data["speed"] = msg.spd_over_grnd * 0.5144
            elif 'GGA' in sentence:
                msg = pynmea2.parse(sentence)
                data["altitude"] = msg.altitude
                no_alt = False
        gps_dat.append(data)
