# -*- coding:utf-8 -*-
# file: base_apiurls
# author: Mundy
# date: 2017/11/13 0013
"""
基本视图相关路由
"""
from django.conf.urls import url
from firstapp.base_views import auth_views, common_views

base_apiurls_map = [
    url(r'^login/', auth_views.LoginView.as_view(), name='login'),  # 登录
    url(r'^logout/', auth_views.LogoutView.as_view(), name='logout'),  # 登录
    url(r'^checkUserInfo/', auth_views.CheckUserInfo.as_view()),  # 判断用户是否登录
    url(r'^getVerify/', auth_views.GetVerify.as_view()),
    url(r'^checkUserIsLogin/', auth_views.CheckUserIsLogin.as_view()),  # 判断用户是否已登录
    url(r'^getNowWeather', common_views.GetNowWeather.as_view())  # 获取天气信息
]