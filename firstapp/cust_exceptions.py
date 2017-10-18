# -*- coding: utf-8 -*-
# __author__ = 'song'
"""
自定义异常，讲后端的异常信息序列化返回给前端

相关接口
===========
"""


from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class SocketUnavailable(APIException):
    """
    socket通信失败异常
    """
    #: 异常响应状态码
    status_code = 503
    #: 异常信息
    default_detail = '通知后台服务程序失败，请检查后台服务是否已运行！'

    @property
    def message(self):
        return self.detail


class CommonError(SocketUnavailable):
    """
    通用错误异常
    """
    default_detail = '操作失败'


class VdpOperationFailed(APIException):
    """
    Vdp操作失败异常
    """
    status_code = 503
    default_detail = '操作失败'


def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc)
    # Now add the HTTP status code to the response.
    if response is not None and isinstance(exc, SocketUnavailable):
        # response.data['status_code'] = response.status_code
        response.data['msg'] = response.data['detail']
    return response


class ValidationFailed(APIException):
    """
    数据不合法异常
    """
    status_code = 400
    default_detail = '数据未通过内部验证！请检查数据是否被破坏!'


class NeedRedirectOperatingException(APIException):
    """
    重定向异常
    """
    status_code = 304
    is_set_client_message = False
    error_msg_key = ''
    default_detail = "需要重定向"
    redirect_url = '/'

    def __init__(self, redirect_url="/", is_set_client_message=False, error_msg_key='', default_detail=''):
        self.redirect_url = redirect_url
        self.is_set_client_message = is_set_client_message
        self.default_detail = default_detail
        self.error_msg_key = error_msg_key