# -*- coding:utf-8 -*-
# file: system_settings_apiurls
# author: Mundy
# date: 2017/11/13 0013
"""
系统设置相关路由
"""
from rest_framework import routers
from django.conf.urls import url
import user_admin


route = routers.DefaultRouter()
# 用户权限等管理
route.register(r'users', user_admin.UserAdminSet)