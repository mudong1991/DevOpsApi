# -*- coding:utf-8 -*-
# file: auth_views
# author: Mundy
# date: 2017/10/18 0018
"""
认证相关API接口
"""
import gvcode
import time
from firstapp.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from firstapp import util
from firstapp.base_views import serializers
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.hashers import make_password
from django.middleware.csrf import get_token


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            request_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            request_ip = request.META['REMOTE_ADDR']

        username = request.data.get('username', '')
        password = request.data.get('password', '')
        verify_code = request.data.get('verifyCode', '')

        # 失败次数和锁定时间
        login_fail_limit_times = settings.LOGIN_FAILED_TIMES_LIMIT
        lock_time = settings.LOCK_TIME

        # 响应状态码和数据
        result_code = 1
        result_data = {'result_msg': '', 'need_verify': False}

        # 判断用户是否存在
        exist_user = User.objects.filter(username=username).first()

        # 需要验证码首先验证验证码
        if cache.get('verify_%s' % request_ip) is not None:
            result_data['need_verify'] = True
            verify = cache.get('verify_%s' % request_ip)
            if str(verify).lower() != str(verify_code).lower():
                # 重新生成验证码
                img, code = gvcode.generate()
                img.save(settings.VERIFY_IMG_PATH)
                cache.set('verify_%s' % request_ip, code, 1 * 24 * 60 * 60)
                result_code = 1
                result_data['result_msg'] = '对不起，验证码错误！'
                # 生成验证码
                img, code = gvcode.generate()
                img.save(settings.VERIFY_IMG_PATH)
                cache.set('verify_%s' % request_ip, code, 1 * 24 * 60 * 60)
                result_data['verify_url'] = settings.VERIFY_IMG_URL
                return Response({'result_code': result_code, 'result_data': result_data})
        else:
            result_data['need_verify'] = False

        # 验证码通过判断登录信息
        # 用户不存在
        if not exist_user:
            result_code = 1
            result_data['result_msg'] = '对不起，该用户不存在！'
        # 用户未激活
        elif exist_user.is_active is False:
            result_code = 1
            result_data['result_msg'] = '用户未激活，请联系管理员！'
        # 用户被锁定
        elif cache.get('error_login_lock_%s_%s' % (request_ip, username)):
            time_stmap = cache.get('error_login_lock_%s_%s' % (request_ip, username))
            lock_surplus_second = int(time_stmap) - int(time.time())
            result_code = 2
            result_data['result_msg'] = '用户已经锁定，请%s秒后再试。' % lock_surplus_second
            result_data['lock_surplus_second'] = lock_surplus_second
        else:
            # 登录认证
            user = authenticate(username=username, password=password)
            # 登录失败
            if user is None:
                # 记录登录者的IP和域名
                error_login_data = cache.get('error_login_%s_%s' % (request_ip, username))
                if error_login_data is None:
                    result_code = 1
                    cache.set('error_login_%s_%s' % (request_ip, username), 0, lock_time * 60)
                    result_data['result_msg'] = '登录失败，用户名密码错误！'
                else:
                    new_error_login_data = int(error_login_data) + 1
                    cache.set('error_login_%s_%s' % (request_ip, username), new_error_login_data, lock_time * 60)

                    if new_error_login_data < login_fail_limit_times:
                        result_data['result_msg'] = '账户密码错误，再输入%s次用户将会锁定%s分钟。' \
                                                    % (login_fail_limit_times - new_error_login_data, lock_time)
                        if new_error_login_data > 1:
                            result_data['need_verify'] = True
                    else:
                        # 锁定用户
                        cache.set('error_login_lock_%s_%s' % (request_ip, username), int(time.time()) + lock_time * 60, lock_time * 60)
                        lock_surplus_second = lock_time * 60
                        result_code = 2
                        result_data['result_msg'] = '用户已经锁定，请%s秒后再试。' % lock_surplus_second
                        result_data['lock_surplus_second'] = lock_surplus_second

            # 登录成功
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
                cache.delete('verify_%s' % request_ip)
                cache.delete('error_login_%s_%s' % (request_ip, username))
                result_data['need_verify'] = False
                result_data['sessionid'] = user_obj.sessionid
                result_data['csrftoken'] = get_token(request)

        # 生成验证码
        if result_data["need_verify"]:
            img, code = gvcode.generate()
            img.save(settings.VERIFY_IMG_PATH)
            cache.set('verify_%s' % request_ip, code, 1 * 24 * 60 * 60)
            result_data['verify_url'] = settings.VERIFY_IMG_URL
        else:
            cache.delete('verify_%s' % request_ip)

        return Response({'result_code': result_code, 'result_data': result_data})


class LogoutView(APIView):
    def post(self, request):
        if request.user:
            user_obj = request.user
            user_obj.isonline = 0
            user_obj.save()

        logout(request)
        return Response({'result_code': 0, 'result_data': 'logout success'})


class GetVerify(APIView):
    """
    获取验证码
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            request_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            request_ip = request.META['REMOTE_ADDR']

        verify = cache.get('verify_%s' % request_ip)
        if verify is not None:
            img, code = gvcode.generate()
            img.save(settings.VERIFY_IMG_PATH)
            cache.set('verify_%s' % request_ip, code, 1 * 24 * 60 * 60)
            return Response({'need_verify': True, 'verify_url': settings.VERIFY_IMG_URL})
        else:
            return Response({'need_verify': False, 'verify_url': ''})


class CheckUserInfo(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        user_obj = request.user
        if user_obj and not isinstance(user_obj, AnonymousUser):
            user_data = serializers.UserSerializer(user_obj).data
            user_data['avatar'] = '{scheme}://{host}{path}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=user_data['avatar'])
            return Response({'result_code': 0, 'result_data': user_data})
        else:
            return Response({'result_code': 1, 'result_data': None})


class CheckUserIsLogin(APIView):
    """
    检查用户是否已经登录
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        if request.COOKIES.has_key('sessionid'):
            session_key = request.COOKIES['sessionid']
            if not isinstance(request.user, AnonymousUser) and session_key != request.user.sessionid:
                return Response({'result_code': 1, 'result_data': 'yes'})
            else:
                return Response({'result_code': 0, 'result_data': 'no'})
        else:
            return Response({'result_code': 0, 'result_data': 'no_sessionid'})


class CheckUserPassword(APIView):
    """
    检查用户密码
    """
    def post(self, request):
        user_password = request.data.get('password', '')
        if not isinstance(request.user, AnonymousUser):
            user = authenticate(username=request.user.username, password=user_password)
            if user is not None:
                return Response({'result_code': 1, 'result_data': 'yes'})
            else:
                return Response({'result_code': 0, 'result_data': 'no'})
        else:
            return Response({'result_code': 0, 'result_data': 'no_auth'})