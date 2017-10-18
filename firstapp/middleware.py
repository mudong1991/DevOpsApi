# -*- coding:utf-8 -*-
# Created by Administrator at 2017/3/7 0007
"""
自定义中间件，对权限、请求响应做一些处理
"""
from io import BytesIO

from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from util import running_log
from util_aes import aes_html_data_decrypt, aes_api_data_encrypt


class CustomAuthorizeMiddleWare(object):
    """
    权限定义中间件
    """
    def process_response(self, request, response):
        """
        HttpResponse重写
        :param request:
        :param response:
        :return:
        """
        #: 页面没有权限的情况处理
        if response.status_code == 403:
            return render(request, 'error_info.html', {"message": "您没有权限访问这个页面！", "status_code": 403}, status=403)
        if response.status_code == 404:
            return render(request, 'error_info.html', {"message": "找不到指定页面！", "status_code": 404}, status=404)

        # api数据加密
        if request.path.startswith("/api/") and settings.API_ENCRYPT:
            if hasattr(response, "content") and hasattr(response, "data"):
                content = response.content

                # 数据加密
                str_encrypted = aes_api_data_encrypt(content)
                response.content = str_encrypted
        return response


class CustomExceptionMiddleWare(object):
    """
    自定义异常处理中间件
    """

    def process_exception(self, request, exception):
        """
        统一处理未捕获的异常
        :param request:
        :param exception:
        :return:
        """
        import exceptions

        # 记录异常
        running_log.error(exception.message or exception)

        # 特殊异常类型处理
        if isinstance(exception, exceptions.IOError):
            if exception.errno == 13:
                exception.message = "您没有权限操作相关文件"

        return render(request, 'error_info.html', {"message": exception.message or exception, "status_code": 500},
                      status=500)


class CustomDecryptMiddleWare(object):
    """
    针对api数据交互解密
    """

    def process_request(self, request):
        url = request.path

        # 对api
        if url.find("api") >= 0 and settings.API_DECRYPT:
            if hasattr(request, 'body') and hasattr(request, '_body'):
                data = request._body
                try:
                    dec_data = aes_html_data_decrypt(data)
                    if dec_data != data:
                        request._body = dec_data
                        request._stream = BytesIO(dec_data)
                except:
                    pass
        # 重定向
        if settings.WEB_URL_PREFIX and settings.WEB_URL_PREFIX in url:
            url = url.split("operations")[1]
            return HttpResponseRedirect(url)
