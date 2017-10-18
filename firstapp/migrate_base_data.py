# -*- coding:utf-8 -*-
# Created migrate_base_data at 2017/3/9 0009
# __author__ = "Mundy"
"""
同步数据库时，初始化部分数据
"""
import threading

from django.conf import settings
from django.contrib.auth.models import *

from firstapp.models import *


def init():
    """
    初始化数据
    :return:
    """
    if AppInstall.objects.filter(name='git').exists():
        return
    # 初始化添加app
    AppInstall.objects.create(name='git', version='2.11.0', app_image='/media/app_images/git.jpg')
    AppInstall.objects.create(name='docker', version='1.7.1', app_image='/media/app_images/docker.jpg')
    AppInstall.objects.create(name='jdk', version='1.8.0_131', app_image='/media/app_images/jdk.jpg')
    AppInstall.objects.create(name='redis', version='3.2.8', app_image='/media/app_images/redis.jpg')
    AppInstall.objects.create(name='mysql', version='5.6.35', app_image='/media/app_images/mysql.jpg')
    AppInstall.objects.create(name='mongodb', version='3.3.3', app_image='/media/app_images/mongodb.jpg')
    AppInstall.objects.create(name='zookeeper', version='3.4.10', app_image='/media/app_images/zookeeper.jpg')
    AppInstall.objects.create(name='kafka', version='0.10.2.1', app_image='/media/app_images/kafka.jpg')
    AppInstall.objects.create(name='nginx', version='1.8.1', app_image='/media/app_images/nginx.jpg')
    AppInstall.objects.create(name='consul', version='2.11.1', app_image='/media/app_images/consul.jpg')
    AppInstall.objects.create(name='maven', version='3.5.0', app_image='/media/app_images/maven.jpg')


def thread_init(sender, **kwargs):
    """
    第一个参数必须是sender，且必须有kwargs参数

    :param sender:
    :param kwargs:
    :return:
    """
    # 在另一个线程中执行init方法，主要是为了解决数据库事务提交延迟的问题。
    t = threading.Timer(1, init)

    t.start()
