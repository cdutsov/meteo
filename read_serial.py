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


class MyThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(MyThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class GPS:
    gps_dat_list = []
    gps_signal_lost = True

    def __init__(self):
        # init gps
        self.gps_serial = serial.Serial('/dev/ttyS0', 9600, timeout=1)

        self.thread = MyThread(target=self.start, args=self.gps_serial)

        self.thread.start()

    def start(self, ser):
        while not self.thread.stopped():
            no_spd = True
            no_alt = True
            data = {}
            lock = threading.Lock()
            lock.acquire()
            print "GPS started!"
            lock.release()
            while no_alt or no_spd:
                sentence = ser.readline().split('$')
                print sentence
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
            self.append_gps(data)

    def stop(self):
        if self.thread.isAlive():
            self.thread.stop()

    @classmethod
    def clear_data(cls):
        cls.gps_dat_list = []

    def append_gps(self, data):
        if not data["longitude"] or data["latitude"] == 0:
            self.gps_dat_list.append(data)
            if self.gps_signal_lost:
                print datetime.datetime.now().isoformat(), "GPS signal acquired!"
            self.gps_signal_lost = False
        else:
            if not self.gps_signal_lost:
                print datetime.datetime.now().isoformat(), "GPS signal lost!"
            self.gps_signal_lost = True
