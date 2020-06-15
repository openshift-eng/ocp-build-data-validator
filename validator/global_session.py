import requests

request_session = None


def set_global_session():
    global request_session
    if not request_session:
        request_session = requests.Session()
