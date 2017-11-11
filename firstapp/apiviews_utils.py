# -*- coding:utf-8 -*-
# file: util
# author: Mundy
# date: 2017/11/1 0001
"""
视图相关工具
"""
from rest_framework import status
from rest_framework import filters
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


# 自定义Grid排序
class GridOrderingFilter(filters.OrderingFilter):
    """
    针对Grid的规则自定义排序
    """
    ordering_param = 'sidx'
    ordering_type_param = 'sord'
    ordering_fields = '__all__'

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.
        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        ordering_type = request.query_params.get(self.ordering_type_param)
        order_type_str = ''
        if ordering_type == 'desc':
            order_type_str = '-'
        if params:
            fileds = [order_type_str + param.strip() for param in params.split(',')]
            return fileds
        return self.get_default_ordering(view)