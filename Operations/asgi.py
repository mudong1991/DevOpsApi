# -*- coding:utf-8 -*-
# file: asgi
# author: Mundy
# date: 2017/9/4 0004
"""
"""
import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Operations.settings")    # 这里填的是你的配置文件settings.py的位置
channel_layer = channels.asgi.get_channel_layer()