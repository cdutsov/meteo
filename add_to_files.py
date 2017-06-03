import os

import datetime

import gpxpy
import gpxpy.gpx

from Adafruit_BME280 import *
import paho.mqtt.client as paho
import veml6070
import time

from dani import post_update
from read_serial import get_dust_particles, get_gps
import pickle

broker = "127.0.0.1"
port = 1883
filename = datetime.datetime.now().isoformat() + ".log"
data = {}


def on_publish(client, userdata, result):  # create function for callback
    # print("data published \n")
    pass


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

    #gpx file
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    # gpx.extensions = "temp"

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    data_list = []
    particles_mean = []

    start_time = datetime.datetime.now()

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
        data["dust_particles"] = particles_set[len(particles_set) // 2]

        gps_dat = get_gps()
        if gps_dat:
            data.update(gps_dat)
        print data
        data_list.append(data)
        publish_data(client=client1, data=data)
        post_update(latitude=data["latitude"], longitude=data["longitude"], timestamp=data["datetime"])

        # Create points:
        point = gpxpy.gpx.GPXTrackPoint(data["latitude"],
                                data["longitude"],
                                elevation=data["altitude"],
                                time=datetime.datetime.now().isoformat())
        point.extensions = data
        gpx_segment.points.append(point)
        if(datetime.datetime.now() - start_time) > datetime.timedelta(seconds=10):
            start_time = datetime.datetime.now()
            with open("track" + datetime.datetime.now().isoformat(), "w") as f:
                print "GPX file printed!"
                f.write(gpx.to_xml(version="1.1"))

main()
