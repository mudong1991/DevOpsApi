# -*- coding:utf-8 -*-
# file: rancher_api
# author: Mundy
# date: 2017/9/1 0001
"""
rancher api调用
"""
import json
import requests
from django.conf import settings

# --------requests设置--------
time_out = 8
headers = {
    'content-type': 'application/json',
    'Accept': 'application/json',
}


def get_response_json(response):
    return response.json()


# 调用receiver_hooks api
def request_receiver_hooks(request_url, data):
    request_s = requests.Session()
    request_s.headers.update(headers)
    request_s.verify = False
    response = request_s.post(request_url, json.dumps(data), timeout=time_out)
    if response.status_code == 200:
        return True
    else:
        return False


def get_rancher_data(request_url, access_key, secret_key):
    request_session = requests.Session()
    request_session.auth = (access_key, secret_key)
    request_session.headers.update(headers)
    request_session.verify = False

    response = request_session.get(request_url, timeout=time_out)

    if response.status_code == 200:
        return get_response_json(response)
    else:
        return ''
