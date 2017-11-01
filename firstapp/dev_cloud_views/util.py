# -*- coding:utf-8 -*-
# file: util
# author: Mundy
# date: 2017/11/1 0001
"""
视图相关工具
"""
from rest_framework import status
from rest_framework.response import Response


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
            return Response(e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return _wrapper