import json
import os

import datetime
import threading

import gpxpy
import gpxpy.gpx

from Adafruit_BME280 import *
import paho.mqtt.client as paho
import veml6070
import time

from external_tracker import post_update, TRACKER_URL
from read_serial import get_dust_particles, GPS
import pickle
import serial
from subprocess import call

broker = "127.0.0.1"
port = 1883
filename = datetime.datetime.now().isoformat() + ".log"
data = {}

gps_data_list = []
gps = GPS()


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


def on_publish(client, userdata, result):  # create function for callback
    # print("data published \n")
    pass


def publish_sensor_data(client, sensor_data):
    client.publish("sensors/temperature", "%0.3f" % (sensor_data["temperature"]), retain=True)
    client.publish("sensors/pressure", "%0.3f" % sensor_data["pressure"])
    client.publish("sensors/humidity", "%0.3f" % sensor_data["humidity"])
    client.publish("sensors/dewpoint", "%0.3f" % sensor_data["dew_point"])
    client.publish("sensors/uv", "%0.3f" % sensor_data["uv"])
    client.publish("sensors/uv_raw", "%0.3f" % sensor_data["uv_raw"])
    client.publish("sensors/dust_particles", "%0.3f" % sensor_data["dust_particles"])


def init_mqtt_client():
    client = paho.Client("control1")  # create client object
    client.on_publish = on_publish  # assign function to callback
    client.connect(broker, port)  # establish connection
    return client


def publish_gps_data(client, gps_data, point_number):
    template = generate_template(gps_data)
    pld = {"name": "point" + str(point_number), "lat": gps_data["latitude"], "lon": gps_data["longitude"], "radius": 2,
           "command": {"lat": gps_data["latitude"], "lon": gps_data["longitude"], "zoom": 18}}
    client.publish('gps/worldmap', payload=json.dumps(pld, indent=2))
    client.publish("template/html_template", "<div ng-bind-html=\"msg.payload\"> "
                   + template + "</div>")


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


def generate_template(gps_dat):
    return "Longitude: " + str(gps_dat["longitude"]) + \
           "<br> Latitude: " + str(gps_dat["latitude"]) + \
           "<br> Speed over ground: " + str(gps_dat["speed"]) + \
           "<br> Altitude: " + str(gps_dat["altitude"]) + "<br>"


def get_sensor_data(sensor, veml):
    data["datetime"] = datetime.datetime.now()
    data["temperature"] = round(sensor.read_temperature(), 2)
    data["pressure"] = round(sensor.read_pressure() / 100, 3)
    data["humidity"] = round(sensor.read_humidity(), 2)
    data["dew_point"] = round(sensor.read_dewpoint(), 2)
    data["uv_raw"] = round(veml.get_uva_light_intensity_raw(), 3)
    data["uv"] = round(veml.get_uva_light_intensity(), 3)
    data["dust_particles"] = round(get_dust_particles(), 2)
    return


def smooth_data(particles_mean):
    particles_mean.append(data["dust_particles"])
    if len(particles_mean) > 9:
        del particles_mean[0]
    particles_set = list(particles_mean)
    particles_set.sort()
    particles = particles_set[len(particles_set) // 2]
    data["dust_particles"] = particles if particles else 0
    return


def post_external(data, data_published_time, update_interval):
    if (datetime.datetime.now() - data_published_time) > datetime.timedelta(seconds=update_interval):
        try:
            post_update(latitude=data["latitude"], longitude=data["longitude"], timestamp=data["datetime"])
            print "data posted to: " + TRACKER_URL
            return datetime.datetime.now()
        except:
            print datetime.datetime.now().isoformat() + "\tNo route to host: " + TRACKER_URL
            return datetime.datetime.now()
    return data_published_time


def speed_based_interval(speed):
    if speed > 0.5:
        update_interval = 20
    else:
        update_interval = 120
    return update_interval


def init_data_file(filename):
    f = open(filename, 'w')
    f.write("Datetime, Lat, Lon, Alt, Speed, Temp, Hum, Press, DewP, UV\n\r")
    return f


def write_to_csv(data_file, data):
    if not gps.gps_signal_lost:
        data_file.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n\r" %
                    (data['datetime'],
                    data['latitude'],
                    data['longitude'],
                    data['altitude'],
                    data['speed'],
                    data['temperature'],
                    data['humidity'],
                    data['pressure'],
                    data['dew_point'],
                    data['uv_raw']))
    else:
        data_file.write("%s, %s, %s, %s, %s, %s\n\r" %
                        (data['datetime'],
                         data['temperature'],
                         data['humidity'],
                         data['pressure'],
                         data['dew_point'],
                         data['uv_raw']))


def main_loop():
    client = init_mqtt_client()
    bme = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
    veml = veml6070.Veml6070()
    veml.set_integration_time(veml6070.INTEGRATIONTIME_1T)

    # gpx file
    gpx, gpx_segment = new_gpx_file()

    data_list = []
    particles_mean = []

    start_time = datetime.datetime.now()
    data_published_time = datetime.datetime.now()

    i = 0

    fname = '/home/pi/meteo/tracks/raw_data' + datetime.datetime.now().strftime('-%m%d-%H%M')
    data_file = init_data_file(filename=fname)

    while True:
        i += 1

        get_sensor_data(sensor=bme, veml=veml)
        smooth_data(particles_mean)
        data_list.append(data)

        # Publish sensor data to MQTT server
        publish_sensor_data(client=client, sensor_data=data)
        write_to_csv(data_file, data)

        # Push data file to server @krasi
        call(["scp", "-P 2020", fname, "chavdar@62.44.98.23:/home/chavdar/Programs/meteo-data/"])

        if not gps.gps_signal_lost:
            for gps_dat in gps.gps_dat_list:
                data.update(gps_dat)

                write_to_csv(data_file, data)

                # Push data file to server @krasi
                call(["scp", "-P 2020", fname, "chavdar@62.44.98.23:/home/chavdar/Programs/meteo-data/"])

                # Publish on MQTT server
                update_interval = speed_based_interval(speed=gps_dat["speed"])

                # Post to external tracker
                data_published_time = post_external(data, data_published_time, update_interval)
                publish_gps_data(client=client, gps_data=gps_dat, point_number=i)

                # Create points in GPX file:
                point = gpxpy.gpx.GPXTrackPoint(data["latitude"],
                                                data["longitude"],
                                                elevation=data["altitude"],
                                                time=datetime.datetime.now())
                point.extensions = dict(data)
                gpx_segment.points.append(point)
            if (datetime.datetime.now() - start_time) > datetime.timedelta(minutes=10):
                start_time = datetime.datetime.now()
                fn = "/home/pi/meteo/tracks/track" + datetime.datetime.now().strftime("-%d%m-%H%M") + ".gpx"
                with open(fn, "w") as f:
                    print datetime.datetime.now().isoformat(), "GPX file printed! Filename: " + fn
                    f.write(gpx.to_xml(version="1.1"))
                gpx, gpx_segment = new_gpx_file()

            gps.clear_data()

        time.sleep(3)


try:
    main_loop()
except:
    gps.stop()
    raise
