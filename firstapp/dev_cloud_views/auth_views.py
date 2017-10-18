# -*- coding:utf-8 -*-
# file: auth_views
# author: Mundy
# date: 2017/10/18 0018
"""
认证相关API接口
"""
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def catch_exception_response(func):
    """
    装饰器函数，捕获函数方法中发生的异常，返回给前端正常的消息提示

    :param func: 接收一个函数
    :return: 响应Response对象

    发生其他异常时，响应前端异常信息。
    """

    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            return Response({"msg": e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return _wrapper


class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']

        print 'aaaa'
        return Response({'ok'})
