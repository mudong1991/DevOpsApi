# -*- coding:utf-8 -*-
# file: tasks
# author: Mundy
# date: 2017/6/2 0002
"""
创建celery任务
"""
import re
import uuid
import logging
import urllib
import time
from urlparse import urlparse
from celery import task, shared_task
from firstapp.salt_api import saltapi_manager
from firstapp import models

celery_task_log = logging.getLogger("info")
# 基础目录
base_path = '/tmp/' + str(uuid.uuid1()) + '/'


# 自动项目部署任务
@shared_task
def deploy_java_project(salt_master_dict, project_docker_id):
    start_time = time.clock() # 开始时间

    # 项目Docker信息
    project_docker_obj = models.ProjectDockerInfo.objects.get(id=project_docker_id)
    # 项目信息
    project_obj = project_docker_obj.project
    minion_id = project_docker_obj.salt_minion.minion_id
    is_start_container = project_docker_obj.is_start_service

    repo_url = project_obj.lib_url.encode('utf-8')
    repo_branch = project_obj.lib_branch if project_obj.lib_branch else ""
    repo_username = project_obj.lib_username
    repo_password = project_obj.lib_password
    repo_project_path = project_obj.lib_path.encode("utf-8") if project_obj.lib_path else ""
    repo_project_deploy_path = project_obj.lib_deploy_path.encode('utf-8') if project_obj.lib_deploy_path else ""
    deploy_port = str(project_obj.deploy_port).encode('utf-8') if project_obj.deploy_port else ""

    # 保存进度和详情的工具类
    class ProjectDeployRecord(object):
        def __init__(self, project_docker):
            self.project_docker = project_docker
            self.project_docker.status = '1'
            self.project_docker.progress = 3
            self.project_docker.save()

        def start_record(self, project_deploy_info, message):
            project_deploy_info.content += "<br/>%s " % message
            project_deploy_info.save()

        def success_record(self, project_deploy_info, deploy_progress_step, message, is_step_end=False, all_end=False):
            """
            记录成功信息
            :param project_deploy_info: 项目部署信息模型对象
            :param deploy_progress_step: 增加的进度（int型）
            :param message: 信息
            :param is_step_end: 是否该步骤结束
            :param is_step_end: 是否全部结束
            :return:
            """
            # 保存进度信息
            self.project_docker.progress += int(deploy_progress_step)
            if all_end:
                # 完成后删除目录
                saltapi_manager.minion_run(salt_master_dict['api_url'],
                                           salt_master_dict['username'],
                                           salt_master_dict['password'],
                                           salt_master_dict['eauth'],
                                           minion_id,
                                           'cmd.run',
                                           "rm -rf %s" % base_path)
                self.project_docker.status = '2'
                end_time = time.clock()
                used_time = str(round(end_time - start_time, 2))
                self.project_docker.time_consume = used_time
            self.project_docker.save()
            # 保存进度详情
            if is_step_end:
                project_deploy_info.step_status = 1
            project_deploy_info.content += "<br/><span style='color:white'>%s</span>" % str(message)
            project_deploy_info.save()

        def failure_record(self, project_deploy_info, message):
            """
            记录失败信息
            :param project_deploy_info: 项目部署信息模型对象
            :param message: 消息信息
            :return:
            """
            # 保存进度信息
            self.project_docker.status = '3'
            self.project_docker.save()
            # 保存进度详情
            project_deploy_info.step_status = 2
            project_deploy_info.content += "<br/><span style='color:red'>%s</span>" % str(message)
            project_deploy_info.save()

            # 失败后删除目录
            saltapi_manager.minion_run(salt_master_dict['api_url'],
                                       salt_master_dict['username'],
                                       salt_master_dict['password'],
                                       salt_master_dict['eauth'],
                                       minion_id,
                                       'cmd.run',
                                       "rm -rf %s" % base_path)

            celery_task_log.info(message)
            raise Exception(message)

        def minion_cmd_run_record(self, project_deploy_info, deploy_progress_step, minion_id, status, message,
                                  success_message="",
                                  error_keywords=None, success_keywords="", is_step_end=False, all_end=False):
            # 修改状态
            if error_keywords is None:
                error_keywords = []
            if status:
                # minion节点响应信息
                if message[0].has_key(minion_id):
                    minion_salt_response = "...<br/>" + str(message[0][minion_id]).encode('utf-8')
                else:
                    self.failure_record(project_deploy_info, '主机连接失败，请检查！')
                    raise Exception('主机连接失败')
                if [True if keyword in minion_salt_response else False for keyword in error_keywords].count(True) == 0:
                    if success_keywords in minion_salt_response:
                        self.success_record(project_deploy_info, deploy_progress_step,
                                            "<pre readonly style='color:black'>{0}</pre>{1}"
                                            .format(minion_salt_response, success_message),
                                            is_step_end, all_end)
                    else:
                        self.failure_record(project_deploy_info,
                                            "<pre readonly style='color:red'>{0}</pre>".format(minion_salt_response))
                else:
                    self.failure_record(project_deploy_info,
                                        "<pre readonly style='color:red'>{0}</pre>".format(minion_salt_response))
            else:
                self.failure_record(project_deploy_info, message)

        def minion_state_record(self, project_deploy_info, deploy_progress_step, minion_id, status, message,
                                success_message="", is_step_end=False, all_end=False):
            ignore_error_keywords = ['already']

            # 修改状态
            if status:
                # minion节点响应信息
                if message[0].has_key(minion_id):
                    minion_salt_response = message[0][minion_id]
                else:
                    self.failure_record(project_deploy_info, '主机连接失败，请检查！')
                    raise Exception('主机连接失败')

                if isinstance(minion_salt_response, list):
                    self.failure_record(project_deploy_info, minion_salt_response[0])

                elif isinstance(minion_salt_response, str) or isinstance(minion_salt_response, unicode):
                    self.failure_record(project_deploy_info, minion_salt_response)

                elif isinstance(minion_salt_response, dict):
                    error_list = []
                    for item_reponse in minion_salt_response.values():
                        if not item_reponse['result']:
                            if [True if keyword in item_reponse['comment'] else False for keyword in
                                ignore_error_keywords] \
                                    .count(True) == 0:
                                error_list.append({'sls_name': item_reponse['name'].encode(
                                    'utf-8') if item_reponse.has_key('name') else '',
                                                   'sls_comment': item_reponse['comment'].encode('utf-8')})
                    if len(error_list) > 0:
                        self.failure_record(project_deploy_info, '操作出错，详情: %s...' % str(error_list)[:800])

                    else:
                        self.success_record(project_deploy_info, deploy_progress_step,
                                            minion_salt_response if success_message is None else success_message,
                                            is_step_end, all_end)
                else:
                    self.failure_record(project_deploy_info, minion_salt_response)

            else:
                self.failure_record(project_deploy_info, message)

    # 初始化项目部署信息对象，修改状态（部署中）
    models.ProjectDeployInfo.objects.filter(project_docker=project_docker_obj).delete()
    project_deploy_record = ProjectDeployRecord(project_docker_obj)

    # ---------step1：安装系统环境----------------
    project_deploy_info1 = models.ProjectDeployInfo(step=1, step_status=0, title='初始化系统环境',
                                                    content="检测代码仓库...", project_docker=project_docker_obj,
                                                    minion_id=minion_id)
    project_deploy_info1.save()

    # 处理git/svn路由地址
    project_name = ""  # 项目名称
    repo_auth_url = ""  # 仓库的认证地址

    try:
        repo_url_split = urlparse(repo_url)
        # 项目名称
        project_word_list = repo_url_split.path.split("/")[-1].split(".")[:-1]
        project_name = '.'.join(project_word_list)

        if not re.match(r'^\w+:/{2}\w.+$', repo_url):
            raise Exception("仓库URL地址错误！")

        repo_url_split = repo_url.split("://")
        repo_url_split.insert(1, "://")
        if repo_username or repo_password:
            repo_url_split.insert(2, urllib.quote(repo_username))
            repo_url_split.insert(3, ":" + urllib.quote(repo_password) + "@")

        # 仓库的认证地址
        repo_auth_url = "".join(repo_url_split)
    except Exception as e:
        project_deploy_record.failure_record(project_deploy_info1, "克隆项目代码失败，不是规范的git/svn代码url地址")

    # docker镜像和容器名称
    project_deploy_record.start_record(project_deploy_info1, '检查镜像名...')
    docker_container_name = project_docker_obj.docker_container
    docker_img_name = project_docker_obj.docker_img
    if not docker_img_name:
        project_deploy_record.failure_record(project_deploy_info1, "获取成功，项目Docker镜像为：" + docker_img_name.encode('utf-8'))
    project_path = base_path + project_name + (('/' + repo_project_path) if repo_project_path else "")  # 项目的路径

    # 安装git环境
    project_deploy_record.start_record(project_deploy_info1, '安装git环境...')
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'state.sls',
                                                   'git'
                                                   )
    project_deploy_record.minion_state_record(project_deploy_info1, 4, minion_id, _status,
                                              _message, success_message='git安装成功！')

    # 安装jdk环境
    project_deploy_record.start_record(project_deploy_info1, '检查jdk环境...')
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'state.sls',
                                                   'jdk'
                                                   )
    project_deploy_record.minion_state_record(project_deploy_info1, 4, minion_id, _status,
                                              _message, success_message='jdk安装成功！')
    # master安装maven环境
    project_deploy_record.start_record(project_deploy_info1, '检查maven环境...')
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'state.sls',
                                                   'maven'
                                                   )
    project_deploy_record.minion_state_record(project_deploy_info1, 4, minion_id, _status,
                                              _message, success_message='maven安装成功！')

    # 检测安装docker环境
    project_deploy_record.start_record(project_deploy_info1, '检测docker环境（请自行安装docker环境）...')
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   'docker version'
                                                   )
    project_deploy_record.minion_cmd_run_record(project_deploy_info1, 4, minion_id, _status,
                                                _message, success_keywords='Version', is_step_end=True, success_message='Docker环境检查成功！')

    # -----------------------------------step2：拉取代码-------------------------------------------------------
    project_deploy_info2 = models.ProjectDeployInfo(step=2, step_status=0, title='拉取项目代码',
                                                    content="拉取项目代码中...", project_docker=project_docker_obj, minion_id=minion_id)
    project_deploy_info2.save()

    # 拉取克隆代码
    project_deploy_record.success_record(project_deploy_info2, 2, "mkdir -pv {0}<br/>cd {0}<br/>rm -rf {1}<br/>sudo /usr/local/git/bin/git clone {2} {3}".format(base_path, project_name, ("-b " + repo_branch) if repo_branch else "", repo_auth_url))
    # Git代码库
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                               salt_master_dict['username'],
                               salt_master_dict['password'],
                               salt_master_dict['eauth'],
                               minion_id,
                               'cmd.run',
                               "mkdir -pv {0};cd {0}; rm -rf {1};sudo /usr/local/git/bin/git clone {2} {3}".format(base_path, project_name, ("-b " + repo_branch) if repo_branch else "", repo_auth_url))
    project_deploy_record.minion_cmd_run_record(project_deploy_info2, 10, minion_id, _status,
                                                _message, success_message='拉取代码成功！', error_keywords=['fatal'], is_step_end=True)

    # -----------------------------------step3：打包java项目代码-----------------------------------------------------
    project_deploy_info3 = models.ProjectDeployInfo(step=3, step_status=0, title='生成项目JAR包',
                                                    content="检查pom.xml文件...", project_docker=project_docker_obj, minion_id=minion_id)
    project_deploy_info3.save()
    # 检查pom.xml文件
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'file.file_exists',
                                                   project_path + '/pom.xml'
                                                   )
    if _status:
        if _message[0][minion_id] is True or _message[0][minion_id] == 'True':
            project_deploy_record.success_record(project_deploy_info3, 5, message='检查pom.xml文件成功！')
        else:
            project_deploy_record.failure_record(project_deploy_info3, message='目录%s中没有找到pom.xml文件！' % project_path)
    else:
        project_deploy_record.failure_record(project_deploy_info3, message='没有找到pom.xml文件！')

    # 清理项目jar包
    project_deploy_record.start_record(project_deploy_info3, '清理jar包...')
    project_deploy_record.success_record(project_deploy_info3, 6, "export PATH=$PATH:/usr/local/jdk/bin/<br/>cd {0}<br/>sudo rm -rf /root/.m2/repository/com/<br/>/usr/local/maven3/bin/mvn clean".format(project_path))
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "export PATH=$PATH:/usr/local/jdk/bin/; cd {0};sudo rm -rf /root/.m2/repository/com/;/usr/local/maven3/bin/mvn clean".format(project_path)
                                                   )
    project_deploy_record.minion_cmd_run_record(project_deploy_info3, 6, minion_id, _status,
                                                _message, success_keywords='BUILD SUCCESS', success_message='清理成功！')
    # 生成项目jar包
    project_deploy_record.start_record(project_deploy_info3, '生成jar包...')
    project_deploy_record.success_record(project_deploy_info3, 2,
                                         "/usr/local/maven3/bin/mvn install".format(
                                             project_path))
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "export PATH=$PATH:/usr/local/jdk/bin/; cd {0}; /usr/local/maven3/bin/mvn install".format(
                                                       project_path)
                                                   )
    project_deploy_record.minion_cmd_run_record(project_deploy_info3, 8, minion_id, _status,
                                                _message,  success_keywords='BUILD SUCCESS', success_message='生成成功！',
                                                )
    # 分析mvn信息获取jar包路径
    project_deploy_record.start_record(project_deploy_info3, '获取jar包路径...')
    deploy_jar_path = ""
    if _status:
        mvn_install_str = _message[0][minion_id]
        result_path_list = list(re.findall(r'.*Building jar: (.*)', mvn_install_str))
        no_sources_path_list = filter(lambda item: 'sources' not in item, result_path_list)
        deploy_jar_path_list = list(filter(lambda item: repo_project_deploy_path in item, no_sources_path_list))

        if deploy_jar_path_list:
            deploy_jar_path = deploy_jar_path_list[0]
            _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                           salt_master_dict['username'],
                                                           salt_master_dict['password'],
                                                           salt_master_dict['eauth'],
                                                           minion_id,
                                                           'file.file_exists',
                                                           "{0}".format(deploy_jar_path)
                                                           )
            if _status:
                if _message[0][minion_id] is True or _message[0][minion_id] == 'True':
                    project_deploy_record.success_record(project_deploy_info3, 6, message='获取成功！即将部署的jar包为:' + deploy_jar_path.encode('utf-8'), is_step_end=True)
                else:
                    project_deploy_record.failure_record(project_deploy_info3, message='获取jar路径失败！')
            else:
                project_deploy_record.failure_record(project_deploy_info3, message='主机连接失败')
        else:
            project_deploy_record.failure_record(project_deploy_info3, message='获取jar路径失败！')
    else:
        project_deploy_record.failure_record(project_deploy_info3, _message)

    # ---------step4：构建Docker镜像----------------
    project_deploy_info4 = models.ProjectDeployInfo(step=4, step_status=0, title='构建Docker镜像',
                                                    content="生成Dockerfile...", project_docker=project_docker_obj, minion_id=minion_id)
    project_deploy_info4.save()
    # 删除原来的镜像和容器
    project_deploy_record.start_record(project_deploy_info4, '删除旧的容器和镜像...')
    project_deploy_record.success_record(project_deploy_info4, 2,
                                         "sudo docker stop %s<br/>sudo docker rm -f %s<br/>sudo docker ps -a | awk '{ print $1,$2 }' | grep  %s| awk '{print $1 }' | xargs -I {} sudo docker rm {}<br/>docker rmi -f %s<br/>" % (
                                             docker_container_name, docker_container_name, docker_img_name,
                                             docker_img_name))
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "sudo docker stop %s;sudo docker rm -f %s;sudo docker ps -a | awk '{ print $1,$2 }' | grep  %s| awk '{print $1 }' | xargs -I {} sudo docker rm {};docker rmi -f %s;" % (
                                                       docker_container_name, docker_container_name,
                                                       docker_img_name, docker_img_name)
                                                   )
    project_deploy_record.minion_cmd_run_record(project_deploy_info4, 6, minion_id, _status,
                                                _message, success_message='删除成功！')

    # 生成Dockerfile
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "\cp {0} {1};cd {1};sudo echo -e 'FROM daocloud.io/java\nADD {2} "
                                                   "/var/www/\nWORKDIR /var/www/\n"
                                                   "CMD java -Duser.timezone=GMT+8 -Xms512M -Xmx1024M -Xmn246M -jar {2}"
                                                   "' > {3}; cat Dockerfile".format(deploy_jar_path, project_path, deploy_jar_path.split("/")[-1], project_path + '/Dockerfile')
                                                   )
    project_deploy_record.success_record(project_deploy_info4, 2,
                                         "cd {0}<br/>cat Dockerfile".format(project_path))
    project_deploy_record.minion_cmd_run_record(project_deploy_info4, 4, minion_id, _status,
                                                _message, error_keywords=['error'], success_message='生成Dockerfile成功！')
    # 构建项目的docker镜像
    project_deploy_record.start_record(project_deploy_info4, '生成镜像中...')
    project_deploy_record.success_record(project_deploy_info4, 2,
                                          "cd %s<br/>sudo docker build -t %s ./" % (project_path, docker_img_name))
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "cd %s; sudo docker build -t %s ./" % (project_path,docker_img_name)
                                                   )
    project_deploy_record.minion_cmd_run_record(project_deploy_info4, 8, minion_id, _status,
                                                _message, success_keywords="Successfully built", success_message='构建镜像成功！')
    project_deploy_record.start_record(project_deploy_info4, '检查镜像{0}...'.format(docker_img_name.encode("utf-8")))
    _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                   salt_master_dict['username'],
                                                   salt_master_dict['password'],
                                                   salt_master_dict['eauth'],
                                                   minion_id,
                                                   'cmd.run',
                                                   "sudo docker images"
                                                   )
    if is_start_container:
        project_deploy_record.minion_cmd_run_record(project_deploy_info4, 2, minion_id, _status,
                                                    _message, success_keywords=docker_container_name.encode("utf-8"),
                                                    success_message='检查镜像{0}成功！'.format(docker_container_name.encode("utf-8")),
                                                    is_step_end=True
                                                    )
        # ---------step5：运行项目Docker容器----------------

        project_deploy_info5 = models.ProjectDeployInfo(step=5, step_status=0, title='运行项目Docker容器',
                                                        content="杀死端口进程...", project_docker=project_docker_obj,
                                                        minion_id=minion_id)
        project_deploy_info5.save()
        # 杀死端口进程
        project_deploy_record.success_record(project_deploy_info5, 2,
                                             "sudo kill -9 $(netstat -tlnp | grep :%s | awk '{print $7}' | awk -F '/' '{print $1}')" % (
                                             deploy_port if deploy_port else 0))
        _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                       salt_master_dict['username'],
                                                       salt_master_dict['password'],
                                                       salt_master_dict['eauth'],
                                                       minion_id,
                                                       'cmd.run',
                                                       "sudo kill -9 $(netstat -tlnp | grep :%s | awk '{print $7}' | awk -F '/' '{print $1}')" % (
                                                       deploy_port if deploy_port else 0)
                                                       )
        project_deploy_record.minion_cmd_run_record(project_deploy_info5, 2, minion_id, _status,
                                                    _message, success_message='杀死端口进程成功！')


        # 运行容器
        deploy_docker_run_str = project_obj.deploy_docker_run.encode(
            'utf-8') if project_obj.deploy_docker_run else ""
        project_deploy_record.start_record(project_deploy_info5, "启动容器...<br/>sudo " + deploy_docker_run_str)
        _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                       salt_master_dict['username'],
                                                       salt_master_dict['password'],
                                                       salt_master_dict['eauth'],
                                                       minion_id,
                                                       'cmd.run',
                                                       'sudo ' + deploy_docker_run_str
                                                       )

        # --------------------运行回调事务-----------------------------------
        if project_obj.success_image_callback:
            # 保存上一个进度
            project_deploy_record.minion_cmd_run_record(project_deploy_info5, 3, minion_id, _status,
                                                        _message, error_keywords=['Error'], success_message='运行容器成功！',
                                                        is_step_end=True)
            # 回调step
            project_deploy_info6 = models.ProjectDeployInfo(step=6, step_status=0, title='运行回调操作',
                                                            content="执行命令...<br/>" + project_obj.success_image_callback.encode('utf-8'), project_docker=project_docker_obj,
                                                            minion_id=minion_id)
            _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                           salt_master_dict['username'],
                                                           salt_master_dict['password'],
                                                           salt_master_dict['eauth'],
                                                           minion_id,
                                                           'cmd.run',
                                                           project_obj.success_image_callback
                                                           )
            project_deploy_record.minion_cmd_run_record(project_deploy_info6, 3, minion_id, _status,
                                                        _message, success_message='执行成功！', is_step_end=True,
                                                        all_end=True)

        else:
            project_deploy_record.minion_cmd_run_record(project_deploy_info5, 6, minion_id, _status,
                                                        _message, success_message='运行容器成功！',
                                                        is_step_end=True, all_end=True)

    else:
        # --------------------运行回调事务-----------------------------------
        if project_obj.success_image_callback:
            # 保存上一个进度
            project_deploy_record.minion_cmd_run_record(project_deploy_info4, 9, minion_id, _status,
                                                        _message,
                                                        success_keywords=docker_container_name.encode("utf-8"),
                                                        success_message='检查镜像{0}成功！'.format(
                                                            docker_container_name.encode("utf-8")),
                                                        is_step_end=True
                                                        )
            # 回调step
            project_deploy_info5 = models.ProjectDeployInfo(step=5, step_status=0, title='运行回调操作',
                                                            content="执行命令...<br/>" + project_obj.success_image_callback.encode(
                                                                'utf-8'), project_docker=project_docker_obj,
                                                            minion_id=minion_id)
            _status, _message = saltapi_manager.minion_run(salt_master_dict['api_url'],
                                                           salt_master_dict['username'],
                                                           salt_master_dict['password'],
                                                           salt_master_dict['eauth'],
                                                           minion_id,
                                                           'cmd.run',
                                                           project_obj.success_image_callback
                                                           )
            project_deploy_record.minion_cmd_run_record(project_deploy_info5, 3, minion_id, _status,
                                                        _message, success_message='执行成功！', is_step_end=True,
                                                        all_end=True)
        else:
            project_deploy_record.minion_cmd_run_record(project_deploy_info4, 12, minion_id, _status,
                                                        _message,
                                                        success_keywords=docker_container_name.encode("utf-8"),
                                                        success_message='检查镜像{0}成功！'.format(
                                                            docker_container_name.encode("utf-8")),
                                                        is_step_end=True, all_end=True
                                                        )