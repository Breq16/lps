import sys

import requests


def get_state(host=sys.argv[1], port=5000):
    return requests.get(f"http://{host}:{port}/state").json()
