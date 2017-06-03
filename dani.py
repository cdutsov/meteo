import serial
import pynmea2
import os
from Adafruit_BME280 import *
import paho.mqtt.client as paho
import veml6070
import time
from read_serial import *
from add_to_files import *
import pickle
import json

with open("/home/pi/dani.json", "aw") as fp:
    json.dump(data, fp)
