# -*- coding:utf-8 -*-
# file: common_views
# author: Mundy
# date: 2017/11/1 0001
"""
通用型的接口
"""
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


# --------requests设置--------
time_out = 16
headers = {
    'content-type': 'application/json',
    'Accept': 'application/json',
}
request_session = requests.Session()
request_session.headers.update(headers)
request_session.verify = False


class GetNowWeather(APIView):
    def get(self, request):
        location_ip = request.GET.get('location_ip', '')
        print settings.HEWEATHER_URL
        response = request_session.get(settings.HEWEATHER_URL + location_ip.encode('utf-8'), timeout=time_out)
        if response.status_code == 200:
            return Response({'result_code': 0, 'result_data': response.json()})
        else:
            raise Exception('获取天气信息失败！')