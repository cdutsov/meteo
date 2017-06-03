import datetime
from dateutil import tz
import requests
import os
import json

TRACKER_URL = "http://192.168.43.20:5000/api/tracker-sessions/create"
API_KEY = "789g2465543fudois"

tzinfo = tz.tzoffset(None, datetime.timedelta(seconds=10800))


DATA_FILE = 'dump.json'

def init_file():
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, mode='w', encoding='utf-8') as f:
            json.dump([], f)

def save_to_file(json_data):
    init_file()
    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        feeds = json.load(f)

    with open(DATA_FILE, mode='w', encoding='utf-8') as feedsjson:
        feeds.append(json_data)
        json.dump(feeds, feedsjson)


def post_internet(json_data):
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            feeds = json.load(f)
        for feed in feeds:
            requests.post(TRACKER_URL, json=feed)
        os.remove(DATA_FILE)
    requests.post(TRACKER_URL, json=json_data)


def post_update(latitude, longitude, timestamp):
    start_ts = end_ts = timestamp.replace(tzinfo=tzinfo)
    json_data = {
        'tracker_id': 2,
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
