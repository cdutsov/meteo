import datetime
from dateutil import tz
import requests

TRACKER_URL = "http://192.168.43.20:5000/api/tracker-sessions/create"
API_KEY = "789g2465543fudois"

tzinfo = tz.tzoffset(None, datetime.timedelta(seconds=10800))


def post_update(latitude, longitude, timestamp):
    start_ts = end_ts = timestamp.replace(tzinfo=tzinfo)

    requests.post(TRACKER_URL, json={
        'tracker_id': 2,
        'start_ts': str(start_ts),
        'end_ts': str(end_ts),
        'sessions': [{
            'latitude': latitude,
            'longitude': longitude
        }],
        'api_key': API_KEY
    })
