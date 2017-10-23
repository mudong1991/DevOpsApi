# -*- coding:utf-8 -*-
# file: auth_views
# author: Mundy
# date: 2017/10/18 0018
"""
认证相关API接口
"""
from firstapp.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firstapp import util
from firstapp import serializers


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


class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        verifyCode = request.data.get('verifyCode', '')

        # 响应状态码和数据
        result_code = 1
        result_data = ''

        # 判断用户是否存在
        exist_user = User.objects.filter(username=username).first()

        # 用户不存在
        if not exist_user:
            result_code = 1
            result_data = '对不起，该用户不存在！'
        elif exist_user.is_active is False:
            result_code = 1
            result_data = '用户已经被锁定，请联系管理员！'
        else:
            # 登录认证
            user = authenticate(username=username, password=password)
            # 登录失败
            if user is None:
                result_code = 1
                result_data = '登录失败，用户名密码错误！'
                # 记录登录者的IP和域名

            else:
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)

                # 保存用户登录信息
                user_obj = User.objects.get(id=exist_user.id)
                user_obj.last_login = util.get_current_time()
                user_obj.isonline = 1
                user_obj.sessionid = request.session.session_key  # 必须要先login登录完成，才会生成session_key
                user_obj.login_times += 1
                user_obj.save()

                result_code = 0
                result_data = {'user_id': user_obj.id, 'user_name': user_obj.username, 'session_id': user_obj.sessionid}

        return Response({'result_code': result_code, 'result_data': result_data})


class GetUserInfoBySession(APIView):
    def get(self, request):
        print request.GET.get('session_id')
        session_id = request.GET.get('session_id')
        user_obj = User.objects.filter(sessionid=session_id).first()
        user_data = serializers.UserSerializer(user_obj).data

        return Response(user_data)


class CheckLoginView(APIView):
    pass