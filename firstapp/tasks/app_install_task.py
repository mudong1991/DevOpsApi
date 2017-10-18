# -*- coding:utf-8 -*-
# file: tasks
# author: Mundy
# date: 2017/6/2 0002
"""
创建celery任务
"""
import time
from celery import task, shared_task
from firstapp.salt_api import saltapi_manager
from firstapp import models


# 安装app封装函数
@shared_task
def salt_minion_install_app(salt_master_dict, salt_minion_id, app_list):
    salt_minion_obj = models.SaltMinion.objects.get(id=salt_minion_id)
    ignore_error_keywords = ['already', 'enabled']

    # 取出一个进行安装（开始）
    for app_install_id in app_list:
        app_install_status_obj = models.AppInstallStatus.objects.filter(salt_minion_id=salt_minion_id,
                                                                        app_install_id=app_install_id).last()
        app_install_status_obj.status = '0'
        app_install_status_obj.save()

        # 请求API
        start_time = time.clock()
        _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                       salt_master_dict['username'],
                                                       salt_master_dict['password'],
                                                       salt_master_dict['eauth'],
                                                       salt_minion_obj.minion_id,
                                                       'state.sls',
                                                       app_install_status_obj.app_install.name
                                                       )
        end_time = time.clock()
        used_time = str(round(end_time - start_time, 2))

        # 修改状态
        if _status:
            # minion节点响应信息
            if _message[0].has_key(salt_minion_obj.minion_id):
                minion_salt_response = _message[0][salt_minion_obj.minion_id]
            else:
                minion_salt_response = '主机连接失败'

            if isinstance(minion_salt_response, list):
                app_install_status_obj.status = '2'
                app_install_status_obj.error_message = minion_salt_response[0]

            elif isinstance(minion_salt_response, str):
                app_install_status_obj.status = '2'
                app_install_status_obj.error_message = minion_salt_response

            elif isinstance(minion_salt_response, dict):
                error_list = []
                for item_reponse in minion_salt_response.values():
                    if not item_reponse['result']:
                        if [True if keyword in item_reponse['comment'] else False for keyword in ignore_error_keywords].count(True) == 0:
                            error_list.append({'sls_name': item_reponse['name'] if item_reponse.has_key('name') else '',
                                               'sls_comment': item_reponse['comment']})
                if len(error_list) > 0:
                    app_install_status_obj.status = '2'
                    app_install_status_obj.error_message = 'sls文件出错，详情: %s' % str(error_list)[:400]

                else:
                    app_install_status_obj.status = '1'
                    app_install_status_obj.error_message = ''
            else:
                app_install_status_obj.status = '2'
                app_install_status_obj.error_message = minion_salt_response

        else:
            app_install_status_obj.status = '2'
            app_install_status_obj.error_message = _message

        app_install_status_obj.used_time = used_time
        app_install_status_obj.save()
