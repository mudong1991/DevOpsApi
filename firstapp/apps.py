# -*- coding:utf-8 -*-
# Created by mudong at 2017/3/7 0007
"""
解决初始化权限问题，在migrate完成后执行一个方法
需要在__init__模块中添加default_app_config = 'firstapp.apps.FirstappConfig'
"""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class FirstappConfig(AppConfig):
    name = 'firstapp'

    def ready(self):
        from firstapp.migrate_base_data import thread_init
        post_migrate.connect(receiver=thread_init, sender=self)