import os

import datetime

import gpxpy
import gpxpy.gpx

from Adafruit_BME280 import *
import paho.mqtt.client as paho
import veml6070
import time

from dani import post_update, TRACKER_URL
from read_serial import get_dust_particles, get_gps
import pickle

broker = "127.0.0.1"
port = 1883
filename = datetime.datetime.now().isoformat() + ".log"
data = {}


def on_publish(client, userdata, result):  # create function for callback
    # print("data published \n")
    pass


def new_gpx_file():
    # gpx file
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    # gpx.extensions = "temp"

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    return gpx, gpx_segment


def publish_data(client, data):
    client.publish("sensors/temperature", "%0.3f" % (data["temperature"]), retain=True)
    client.publish("sensors/pressure", "%0.3f" % data["pressure"])
    client.publish("sensors/humidity", "%0.3f" % data["humidity"])
    client.publish("sensors/dewpoint", "%0.3f" % data["dew_point"])
    client.publish("sensors/uv", "%0.3f" % data["uv"])
    client.publish("sensors/uv_raw", "%0.3f" % data["uv_raw"])
    client.publish("sensors/dust_particles", "%0.3f" % data["dust_particles"])


def append_data(d):
    if os.path.exists(filename):
        with open(filename, "rb") as data_file:
            data_list = pickle.load(data_file)
            data_list.append(d)
        with open(filename, "wb") as data_file:
            pickle.dump(data_list, data_file)
    else:
        with open(filename, "wb") as data_file:
            pickle.dump([], data_file)


def main():
    # config bme sensor
    sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
    tstart = time.time()
    client1 = paho.Client("control1")  # create client object
    client1.on_publish = on_publish  # assign function to callback
    client1.connect(broker, port)  # establish connection
    veml = veml6070.Veml6070()
    veml.set_integration_time(veml6070.INTEGRATIONTIME_1T)

    # gpx file
    gpx, gpx_segment = new_gpx_file()

    data_list = []
    particles_mean = []
    gps_dat = None

    start_time = datetime.datetime.now()
    data_published_time = datetime.datetime.now()

    while True:
        data["datetime"] = datetime.datetime.now()
        data["temperature"] = round(sensor.read_temperature(), 2)
        data["pressure"] = round(sensor.read_pressure() / 100, 3)
        data["humidity"] = round(sensor.read_humidity(), 2)
        data["dew_point"] = round(sensor.read_dewpoint(), 2)
        data["uv_raw"] = round(veml.get_uva_light_intensity_raw(), 3)
        data["uv"] = round(veml.get_uva_light_intensity(), 3)
        data["dust_particles"] = round(get_dust_particles(), 2)
        # data["dust_particles"] = 0
        particles_mean.append(data["dust_particles"])
        if len(particles_mean) > 9:
            del particles_mean[0]
        particles_set = list(particles_mean)
        particles_set.sort()
        particles = particles_set[len(particles_set) // 2]
        data["dust_particles"] = particles if particles else 0

        data_list.append(data)

        publish_data(client=client1, data=data)

        tmp_gps_dat = get_gps()
        if tmp_gps_dat and not tmp_gps_dat["latitude"] == 0:
            gps_dat = tmp_gps_dat
        if gps_dat and not gps_dat["latitude"] == 0:
            data.update(gps_dat)
            if gps_dat["speed"] > 0.5:
                update_interval = 20
            else:
                update_interval = 120

            if (datetime.datetime.now() - data_published_time) > datetime.timedelta(seconds=update_interval):
                data_published_time = datetime.datetime.now()
                try:
                    post_update(latitude=data["latitude"], longitude=data["longitude"], timestamp=data["datetime"])
                except:
                    print datetime.datetime.now().isoformat() + "\tNo route to host: " + TRACKER_URL

            # Create points:
            point = gpxpy.gpx.GPXTrackPoint(data["latitude"],
                                            data["longitude"],
                                            elevation=data["altitude"],
                                            time=datetime.datetime.now())
            point.extensions = dict(data)
            gpx_segment.points.append(point)
            if (datetime.datetime.now() - start_time) > datetime.timedelta(minutes=10):
                start_time = datetime.datetime.now()
                fname = "tracks/track" + datetime.datetime.now().strftime("-%H%M-%d%m") + ".gpx"
                with open(fname, "w") as f:
                    print datetime.datetime.now().isoformat() + "GPX file printed! Fname: " + fname
                    f.write(gpx.to_xml(version="1.1"))
                gpx, gpx_segment = new_gpx_file()


main()
