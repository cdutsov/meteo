import datetime
from dateutil import tz
import requests
import os
import json

TRACKER_URL = "http://192.168.43.20:5000/api/tracker-sessions/create"
API_KEY = "fyu789gf75h46gs"

tzinfo = tz.tzoffset(None, datetime.timedelta(seconds=10800))

DATA_FILE = '/home/pi/meteo/src/dump.json'


def init_file():
    if not os.path.isfile(DATA_FILE):
        print "file initialized..."
        with open(DATA_FILE, mode='w') as f:
            json.dump([], f)


def save_to_file(json_data):
    init_file()
    print "saving to fileas"
    with open(DATA_FILE, mode='r') as f:
        feeds = json.load(f)
    with open(DATA_FILE, mode='w') as feedsjson:
        feeds.append(json_data)
        json.dump(feeds, feedsjson)
    print "now feeds is %s" % len(feeds)

def post_internet(json_data):
    requests.post(TRACKER_URL, json=json_data)
    if os.path.isfile(DATA_FILE):
        print "data file exists"
        with open(DATA_FILE, mode='r') as f:
            feeds = json.load(f)
        print "len is: %s" % len(feeds)
        for i, feed in enumerate(feeds):
            requests.post(TRACKER_URL, json=feed)
            print "posting... %s" % i
        os.remove(DATA_FILE)
    print "internet posted!"


def post_update(latitude, longitude, timestamp):
    start_ts = end_ts = timestamp.replace(tzinfo=tzinfo)
    json_data = {
        'tracker_id': 3,
        'start_ts': str(start_ts),
        'end_ts': str(end_ts),
        'sessions': [{
            'latitude': latitude,
            'longitude': longitude
        }],
        'api_key': API_KEY
    }
    try:
        post_internet(json_data)
    except:
        save_to_file(json_data)
