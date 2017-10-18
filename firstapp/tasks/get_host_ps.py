# -*- coding:utf-8 -*-
# file: get_host_ps
# author: Mundy
# date: 2017/8/9 0009
"""
获取主机进程信息
"""
import logging
import re
from firstapp import models
from firstapp.salt_api import saltapi_manager
from celery import task, shared_task
from django.utils import timezone

celery_task_log = logging.getLogger("info")


@shared_task
def get_host_ps_info(salt_master_dict, salt_minion_id):
    salt_minion_obj = models.SaltMinion.objects.get(id=salt_minion_id)
    minion_id = salt_minion_obj.minion_id
    # 删除旧的数据
    models.HostPs.objects.filter(salt_minion=salt_minion_obj).delete()
    # 查询
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "ps -aeo pid,user,%cpu,%mem,stat,time,command --sort -%mem"
                                                   )
    if _status:
        if _message[0].has_key(minion_id):
            result_info = _message[0][minion_id]
            result_row = result_info.split('\n')
            tmp = []
            for index, row_data in enumerate(result_row):
                if index > 1:
                    row_data_list = re.findall('(\S+)', row_data)
                    result = {'pid': row_data_list[0], 'user': row_data_list[1], 'cpu_rate': row_data_list[2],
                              'mem_rate': row_data_list[3], 'stat': row_data_list[4], 'run_time': row_data_list[5],
                              'command': ' '.join(row_data_list[6:])}
                    if float(result['cpu_rate']) > 0 or float(result['mem_rate']) > 0:
                        tmp.append(result)
            # 保存数据
            for data in tmp:
                models.HostPs.objects.create(salt_minion=salt_minion_obj, view_time=timezone.now(), **data)
        else:
            celery_task_log.error('查询失败！'+_message[0].encode('utf-8'))
            raise Exception('查询失败！'+_message[0].encode('utf-8'))
    else:
        celery_task_log.error('主机连接失败！')
        raise Exception('主机连接失败！')