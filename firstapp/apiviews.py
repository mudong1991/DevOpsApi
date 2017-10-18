# -*- coding:utf-8 -*-
# file: apiviews
# author: Mundy
# date: 2017/5/26 0026
"""
api视图
"""
import time, datetime
import os, sys
import json
import platform
import jenkins
import rancher_api
from django.conf import settings
from django.utils import timezone
from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from firstapp import models
from firstapp import serializers
from firstapp import custom_filters
from firstapp.salt_api import saltapi_manager
from pagination import CustomPagination
from firstapp.util_aes import aes_api_data_encrypt, aes_html_data_decrypt
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseForbidden
from firstapp.util import get_page_result
from rest_framework.viewsets import mixins
from django.shortcuts import render, render_to_response
from django.core.cache import cache
from firstapp import tasks


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
            return Response({"msg": e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return _wrapper


# 自定义Grid排序
class GridOrderingFilter(filters.OrderingFilter):
    """
    针对Grid的规则自定义排序
    """
    ordering_param = 'sidx'
    ordering_type_param = 'sord'
    ordering_fields = '__all__'

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.
        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        ordering_type = request.query_params.get(self.ordering_type_param)
        order_type_str = ''
        if ordering_type == 'desc':
            order_type_str = '-'
        if params:
            fileds = [order_type_str + param.strip() for param in params.split(',')]
            return fileds
        return self.get_default_ordering(view)


class BusinessAdminViewSet(viewsets.ModelViewSet):
    queryset = models.BusinessAdmin.objects.all()
    serializer_class = serializers.BusinessAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name', '$create_user')
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        # 创建一个业务，就给这个业务创建一个名为'空闲机'和'故障机'的内置模块
        serializer.save()
        business_obj = models.BusinessAdmin.objects.get(id=serializer.data['id'])
        models.Module.objects.create(business=business_obj, name='空闲机', description='业务的内置模块-空闲机')
        models.Module.objects.create(business=business_obj, name='故障机', description='业务的内置模块-故障机')

    @list_route(methods=['GET'])
    @catch_exception_response
    def all_business(self, request):
        """
        获取所有的业务
        :param request:
        :return:
        """
        business_list = models.BusinessAdmin.objects.all()
        serializers_list = []
        for business in business_list:
            serializers_list.append(serializers.BusinessAdminSerializer(business).data)
        return Response({'rows': serializers_list})


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = models.Cluster.objects.all()
    serializer_class = serializers.ClusterSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name',)

    @list_route(methods=['POST'])
    @catch_exception_response
    def remove_cluster(self, request):
        cluster_id = request.data.get('cluster_id', 0)
        business_id = request.data.get('business_id', 0)
        try:
            cluster_obj = models.Cluster.objects.get(id=int(cluster_id))
        except Exception as e:
            raise Exception('获取集群信息失败！')

        try:
            business_obj = models.BusinessAdmin.objects.get(id=int(business_id))
        except Exception as e:
            raise Exception('获取业务信息失败！')

        # 获取业务下的空闲模块
        business_free_module = models.Module.objects.filter(business=business_obj, name='空闲机').first()

        # 获取该集群下的所有模块
        module_list = cluster_obj.modules.all()
        # 获取该集群下的所有主机
        for module_obj in module_list:
            host_list = module_obj.salt_minions.all()
            for host_obj in host_list:
                if host_obj.module.all().count() > 1:
                    host_obj.module.remove(module_obj)
                else:
                    host_obj.module = [business_free_module]
            # 删除模块
            module_obj.delete()
        # 删除集群
        cluster_obj.delete()
        return Response({'result_status': True, 'result_data': 'ok'})


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name',)

    @list_route(methods=['GET'])
    @catch_exception_response
    def get_available_module(self, request):
        business_id = request.GET.get('business_id', None) if request.GET.get('business_id', 0) else 0
        try:
            business_obj = models.BusinessAdmin.objects.get(id=business_id)
        except Exception as e:
            raise Exception('没有找到业务信息')
        queryset = models.Module.objects.all().filter(business__id=business_id).exclude(name__in=['故障机', '空闲机'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['POST'])
    @catch_exception_response
    def remove_module(self, request):
        module_id = request.data.get('module_id', 0)
        business_id = request.data.get('business_id', 0)
        try:
            module_obj = models.Module.objects.get(id=int(module_id))
        except Exception as e:
            raise Exception('获取模块信息失败！')
        try:
            business_obj = models.BusinessAdmin.objects.get(id=int(business_id))
        except Exception as e:
            raise Exception('获取业务信息失败！')
        # 获取该模块下的所有主机
        host_list = module_obj.salt_minions.all()

        # 获取业务下的空闲模块
        business_free_module = models.Module.objects.filter(business=business_obj, name='空闲机').first()
        for host_obj in host_list:
            if host_obj.module.all().count() > 1:
                host_obj.module.remove(module_obj)
            else:
                host_obj.module = [business_free_module]

        # 删除模块
        module_obj.delete()
        return Response({'result_status': True, 'result_data': 'ok'})


class ProjectCenterViewSet(viewsets.ModelViewSet):
    queryset = models.ProjectCenter.objects.all().order_by('-pk')
    serializer_class = serializers.ProjectCenterSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name', '$description')
    pagination_class = CustomPagination

    @list_route(methods=['POST'])
    @catch_exception_response
    def deploy_start(self, request):
        # 部署salt_minion的id
        project_id = request.data.get('id', '')
        deploy_salt_minion = request.data.get('deploy_salt_minion', [])
        is_start_service = request.data.get('is_start_service', '')
        deploy_port = request.data.get('deploy_port', '')
        deploy_docker_run = request.data.get('deploy_docker_run', '')
        success_image_callback = request.data.get('success_image_callback', '')

        try:
            project_obj = models.ProjectCenter.objects.get(id=project_id)
        except:
            raise Exception('没有找到项目信息')

        # 检查salt服务配置
        salt_master_obj = models.SaltMaster.objects.last()

        if not salt_master_obj:
            raise Exception('没有找到salt服务配置信息！')
        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            'self_minion_id': salt_master_obj.self_minion_id}
        try:
            project_obj.deploy_salt_minion = [models.SaltMinion.objects.get(id=int(salt_minion_id)) for salt_minion_id
                                              in deploy_salt_minion]
            project_obj.is_start_service = (True if is_start_service == '1' else False)
            project_obj.deploy_port = deploy_port
            project_obj.deploy_docker_run = deploy_docker_run
            project_obj.success_image_callback = success_image_callback
            project_obj.deploy_time = timezone.now()
            project_obj.save()
        except:
            raise Exception('部署信息有误！')

        # 部署的主机列表（salt_minion_id）
        salt_minion_obj_list = [models.SaltMinion.objects.get(id=int(salt_minion_id)) for salt_minion_id
                                              in deploy_salt_minion]
        # 删除旧数据
        models.ProjectDockerInfo.objects.filter(project_id=project_id).delete()

        # 添加docker信息
        try:
            for salt_minion_obj in salt_minion_obj_list:
                new_project_docker = models.ProjectDockerInfo.objects.create(project_id=project_id, salt_minion=salt_minion_obj,
                                                        port=project_obj.deploy_port, docker_img=project_obj.docker_img_name,
                                                        docker_container=project_obj.deploy_container_name,
                                                        deploy_docker_run=project_obj.deploy_docker_run, progress=0, status=0,
                                                        is_start_service=project_obj.is_start_service)
                project_docker_id = new_project_docker.id
                # 启动任务
                tasks.deploy_java_project.delay(salt_master_dict, project_docker_id)
                print '--------------------------'
        except Exception as e:
            print e
            raise Exception('项目部署启动失败，请检查Celery服务是否开启！')

        return Response({'result_status': True, 'result_data': 'ok'})


class ProjectDockerInfoViewSet(viewsets.ModelViewSet):
    queryset = models.ProjectDockerInfo.objects.all()
    serializer_class = serializers.ProjectDockerInfoSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    filter_class = custom_filters.ProjectDockerInfoFilter

    @list_route(methods=['GET'])
    @catch_exception_response
    def get_other_node(self, request):
        project_id = request.GET.get('project_id', '')
        # 当前页数
        page = request.GET.get('page', 1)

        try:
            project_obj = models.ProjectCenter.objects.get(id=project_id)
        except:
            raise Exception('没有找到项目相关信息！')

        if project_obj.deploy_status != '2':
            raise Exception('该项目没有部署成功，不能进行分发部署操作！')
        minion_id = project_obj.deploy_minion_id
        container_name = project_obj.deploy_container_name
        salt_minion_obj = models.SaltMinion.objects.filter(minion_id=minion_id)

        project_docker_filter_obj = models.ProjectDockerInfo.objects.filter(project=project_obj, salt_minion=salt_minion_obj, docker_container=container_name)
        if not project_docker_filter_obj.exists():
            raise Exception('该项目没有部署成功，不能进行分发部署操作！')
        else:
            project_docker_obj = project_docker_filter_obj.first()

        # docker_info_queryset = models.ProjectDockerInfo.objects.filter(project=project_obj).all()
        docker_info_queryset = models.ProjectDockerInfo.objects.filter(project=project_obj).exclude(salt_minion=salt_minion_obj, docker_container=container_name)

        # 分页
        result_data = [serializers.ProjectDockerInfoSerializer(docker_info).data for docker_info in docker_info_queryset]
        page_result_data = get_page_result(data_list=result_data, page=int(page))

        result = page_result_data
        result.update({'project_name': project_obj.name, 'deploy_docker_run': project_docker_obj.deploy_docker_run,
                       'port': project_docker_obj.port,
                       'docker_container': project_docker_obj.docker_container,
                       'docker_img': project_docker_obj.docker_img})
        return Response(result)


class SaltMasterViewSet(viewsets.ModelViewSet):
    queryset = models.SaltMaster.objects.all()
    serializer_class = serializers.SaltMasterSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name', '$api_url', '$username', '$description')
    pagination_class = CustomPagination

    @list_route(methods=['GET'])
    @catch_exception_response
    def get_last_master(self, request):
        """
        获取所有的master主机
        :param request:
        :return:
        """
        salt_master_obj = models.SaltMaster.objects.last()
        if not salt_master_obj:
            return Response({'result_status': False, 'result_data': '没有找到配置信息'})

        return Response({'result_status': True, 'result_data': serializers.SaltMasterSerializer(salt_master_obj).data})

    @detail_route(methods=['GET'])
    @catch_exception_response
    def salt_auth(self, request, pk=None):
        try:
            salt_master_obj = models.SaltMaster.objects.get(id=pk)
        except Exception:
            raise Exception('没有找到salt-master服务！')
        salt_master_info = (
            salt_master_obj.api_url,
            salt_master_obj.username,
            str(aes_html_data_decrypt(str(salt_master_obj.password))) if salt_master_obj.password else '',
            salt_master_obj.eauth,
        )
        result_status, result_data = saltapi_manager.login_salt(*salt_master_info)
        if result_status:
            salt_master_obj.token = result_data
            salt_master_obj.save()
            return Response({'result_status': True, 'result_data': 'ok'})
        else:
            raise Exception('Master服务端[%s]%s' % (str(salt_master_obj.name.encode('utf-8')), str(result_data)))


class SaltMinionViewSet(viewsets.ModelViewSet):
    queryset = models.SaltMinion.objects.all()
    serializer_class = serializers.SaltMinionSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    filter_class = custom_filters.SaltMinionFilter
    search_fields = ('$host_name', '$minion_id')
    pagination_class = CustomPagination

    @list_route(methods=['GET'])
    @catch_exception_response
    def get_all_minion(self, request):
        """
       获取所有的minion主机
       :param request:
       :return:
       """
        module_id = request.GET.get('module_id', '')
        if module_id:
            salt_minion_list = models.SaltMinion.objects.filter(module__id=module_id)
        else:
            salt_minion_list = models.SaltMinion.objects.all()

        serializers_list = []
        for salt_minion in salt_minion_list:
            serializers_list.append(serializers.SaltMinionSerializer(salt_minion).data)
        return Response(serializers_list)

    @list_route(methods=['GET'])
    @catch_exception_response
    def save_minion(self, request):
        salt_master = request.GET.get('salt_master', 0)

        try:
            salt_master_obj = models.SaltMaster.objects.get(id=int(salt_master))
        except Exception as e:
            raise Exception('找不到SaltMaster的相关信息！')

        # 拿到token
        request_url = str(salt_master_obj.api_url)
        token = str(salt_master_obj.token)

        # 获取所有主机信息
        result_status, result_data = saltapi_manager.get_all_host(request_url, token)

        if result_status is False:
            raise Exception('查询失败，原因：%s' % result_data)
        else:
            # 将数据导入到数据库中
            node_data_list = result_data[0]
            for key in node_data_list.keys():
                data_dict = node_data_list[key]
                minion_data = {
                    'salt_master': models.SaltMaster.objects.get(id=int(salt_master)),
                    'online': None,
                    'minion_id': key,
                    'host_name': data_dict['localhost'],
                    'host_osarch': data_dict['osarch'] if data_dict.has_key('osarch') else '',
                    'host_system': data_dict['osfullname'] + data_dict['osrelease'],
                    'host_kernel': data_dict['kernelrelease'],
                    'host_cpu_type': data_dict['cpu_model'],
                    'host_cpu_num': data_dict['num_cpus'],
                    'lan_ip': data_dict['fqdn_ip4'][0] if data_dict['fqdn_ip4'] else '',
                    'wan_ip': data_dict['ip_interfaces']['eth1'][0] if data_dict['ip_interfaces'].has_key(
                        'eth1') else '',
                    'host_mem_total': data_dict['mem_total']
                }
                try:
                    if not models.SaltMinion.objects.filter(minion_id=key).exists():
                        models.SaltMinion.objects.create(**minion_data)
                    else:
                        models.SaltMinion.objects.update(**minion_data)
                except Exception as e:
                    raise Exception('%s查询失败，原因：数据异常！' % data_dict['localhost'].encode('utf-8'))

        return Response({'result_status': True, 'result_data': 'ok'})

    @list_route(methods=['GET'])
    def download_saltminion_setting(self, request):
        """
        salt-minion设置文件下载
        :param request:
        :return:
        """
        reload(sys)
        sys.setdefaultencoding('utf8')

        not_found_rend = render(request, 'error_info.html', {"message": "找不到相关文件！", "status_code": 404})
        # 文件名需要转成系统对应的编码才能识别相应的中文目录
        file_name = 'salt-minion-setting.sh'
        try:
            if platform.system() == 'Windows':
                file_path = os.path.join(settings.MEDIA_ROOT, 'localfiles', file_name.encode('gbk'))
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'localfiles', file_name.encode('utf8'))
        except:
            return not_found_rend

        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            return not_found_rend

        def read_file(fp):
            file = open(fp, 'rb')
            while True:
                c = file.read(1024)
                if c:
                    yield c
                else:
                    break
            file.close()

        response = HttpResponse(read_file(file_path), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(file_name)
        return response

    @detail_route(methods=['GET'])
    @catch_exception_response
    def check_online(self, request, pk=None):
        try:
            host_obj = models.SaltMinion.objects.get(id=int(pk))
            salt_master_obj = host_obj.salt_master
        except Exception as e:
            raise Exception('Minion客户机信息获取失败！')

        try:
            password = str(aes_html_data_decrypt(str(salt_master_obj.password)))
        except Exception as e:
            password = ''

        params = (
            salt_master_obj.api_url,
            salt_master_obj.username,
            password,
            salt_master_obj.eauth,
            str(host_obj.minion_id),
            'test.ping'
        )
        result_status, result_data = saltapi_manager.minion_run(*params)
        if result_status:
            host_obj.online = True
            host_obj.save()
        else:
            host_obj.online = False
            host_obj.save()
        return Response({'result_status': True, 'result_data': 'ok'})

    @detail_route(methods=['POST'])
    @catch_exception_response
    def run_command(self, request, pk=None):
        command = request.data.get('command', '')
        limit_words = request.data.get('limit_words', '')

        try:
            host_obj = models.SaltMinion.objects.get(id=int(pk))
            salt_master_obj = host_obj.salt_master
        except Exception as e:
            raise Exception('主机信息获取失败！')

        try:
            password = str(aes_html_data_decrypt(str(salt_master_obj.password)))
        except Exception as e:
            password = ''

        params = (
            salt_master_obj.api_url,
            salt_master_obj.username,
            password,
            salt_master_obj.eauth,
            str(host_obj.minion_id),
            'cmd.run',
            command,
        )
        result_status, result_data = saltapi_manager.minion_run(*params)

        if result_status:
            if limit_words:
                try:
                    limit_words = int(limit_words)
                except:
                    limit_words = 1000
                result_data_str = result_data[0][str(host_obj.minion_id)][-limit_words:]
            else:
                result_data_str = result_data[0][str(host_obj.minion_id)]

            return Response({'result_status': True, 'result_data': result_data_str,
                             'run_time': datetime.datetime.now().strftime(settings.TIME_FORMAT)})
        else:
            raise Exception(result_data)

    @list_route(methods=['POST'])
    @catch_exception_response
    def allot_business(self, request):
        business_id = request.data.get('business_id', None) if request.data.get('business_id', 0) else 0
        host_id_list = list(request.data.get('host_id_list', []))

        try:
            business_obj = models.BusinessAdmin.objects.get(id=business_id)
        except Exception as e:
            raise Exception('找不到业务信息！')

        for host_id in host_id_list:
            try:
                module_obj = models.Module.objects.filter(business=business_obj, name='空闲机').first()
            except Exception as e:
                raise Exception('没有找打业务的空闲机模块！')

            try:
                host_obj = models.SaltMinion.objects.get(id=host_id)
            except Exception as e:
                raise Exception('没有找到主机信息！')
            host_obj.module = [module_obj]
        return Response({'result_status': True, 'result_data': 'ok'})

    @list_route(methods=['GET'])
    @catch_exception_response
    def tree_framework(self, request):
        business_id = request.GET.get('business_id', None) if request.GET.get('business_id', 0) else 0
        try:
            business_obj = models.BusinessAdmin.objects.get(id=business_id)
        except Exception as e:
            raise Exception('没有找到业务信息')

        # 业务的总主机数（不包含空闲和故障机）
        host_list = []
        all_modules = business_obj.modules.exclude(name__in=['空闲机', '故障机'])
        for module in all_modules:
            host_list += module.salt_minions.all()
        host_unique_list = set([host.id for host in host_list])
        business_host_num = len(host_unique_list)

        # 业务的故障和空闲主机数
        free_module_host_count = business_obj.modules.filter(name='空闲机').first().salt_minions.count() if \
            business_obj.modules.filter(name='空闲机') else 0
        fault_module_host_count = business_obj.modules.filter(name='故障机').first().salt_minions.count() if \
            business_obj.modules.filter(name='故障机') else 0

        # 一级树（业务）
        result_data = {
            'value': {'id': business_id, 'name': business_obj.name, 'host_count': business_host_num,
                      'topology': str(business_obj.topology)},
            'close': False,
            'free_module_host_count': free_module_host_count,
            'fault_module_host_count': fault_module_host_count,
            'listTree': []
        }

        # 二级树（集群）
        if int(business_obj.topology) == 1:
            cluster_list = business_obj.clusters.all()  # 集群列表
            if len(cluster_list) > 0:
                for cluster in cluster_list:
                    module_list = cluster.modules.all()
                    # 集群的总主机数
                    host_list = []
                    for module in module_list:
                        host_list += module.salt_minions.all()
                    host_unique_list = set([host.id for host in host_list])
                    cluster_host_num = len(host_unique_list)
                    cluster_tree = {'value': {'id': cluster.id, 'name': cluster.name, 'host_count': cluster_host_num},
                                    'close': False, 'listTree': []}
                    if len(module_list) > 0:  # 集群下的模块列表
                        for module in module_list:
                            cluster_tree['listTree'].append({'value': {'id': module.id, 'name': module.name,
                                                                       'host_count': module.salt_minions.all().count()}})
                    result_data['listTree'].append(cluster_tree)
        # 二级树（模块）
        else:
            module_list = business_obj.modules.all().exclude(name__in=['空闲机', '故障机'])  # 模块列表
            if len(module_list) > 0:  # 集群下的模块列表
                for module in module_list:
                    result_data['listTree'].append(
                        {'value': {'id': module.id, 'name': module.name, 'host_count': module.salt_minions.all().count()}})

        return Response({'result_status': True, 'result_data': result_data})

    @list_route(methods=['POST'])
    @catch_exception_response
    def module_change(self, request):
        try:
            is_cover = bool(request.data.get('is_cover', True))
            built_in = str(request.data.get('built_in', ''))
            business_id = request.data.get('business_id', None) if request.data.get('business_id', 0) else 0
            host_list = list(request.data.get('host_id', []))
            module_list = list(request.data.get('module_id', []))

            try:
                models.BusinessAdmin.objects.get(id=business_id)
            except Exception as e:
                raise Exception('没有找到业务信息！')

            if built_in == 'free':
                business_free_module = models.Module.objects.filter(business__id=business_id, name='空闲机').first()
                for host_id in host_list:
                    host_obj = models.SaltMinion.objects.get(id=int(host_id))
                    host_obj.module = [business_free_module]
                return Response({'result_status': True, 'result_data': 'ok'})
            elif built_in == 'fault':
                business_fault_module = models.Module.objects.filter(business__id=business_id, name='故障机').first()
                for host_id in host_list:
                    host_obj = models.SaltMinion.objects.get(id=int(host_id))
                    host_obj.module = [business_fault_module]
                return Response({'result_status': True, 'result_data': 'ok'})
            else:
                module_obj_list = [models.Module.objects.get(id=int(module_id)) for module_id in module_list]
                for host_id in host_list:
                    host_obj = models.SaltMinion.objects.get(id=int(host_id))
                    if is_cover:
                        host_obj.module = module_obj_list
                    else:
                        for module_obj in module_obj_list:
                            host_obj.module.add(module_obj)
                return Response({'result_status': True, 'result_data': 'ok'})
        except Exception as e:
            print e
            raise Exception('操作失败，原因: %s' % str(e))

    @list_route(methods=['GET'])
    @catch_exception_response
    def export_execl(self, request):
        business_id = self.request.GET.get('business_id', None)
        cluster_id = self.request.GET.get('cluster_id', None)
        module_id = self.request.GET.get('module_id', None)
        search = self.request.GET.get('search', '')

        business_name = models.BusinessAdmin.objects.get(id=business_id).name if business_id else u''
        cluster_name = models.Cluster.objects.get(id=cluster_id).name if cluster_id else u''
        if module_id == 'free':
            module_name = u'空闲机'
        elif module_id == 'fault':
            module_name = u'故障机'
        else:
            module_name = models.Module.objects.get(id=module_id).name if module_id else u''
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data_query_list = serializer.data
        data_list = []
        for data in data_query_list:
            temp = {
                'host_name': data['host_name'],
                'business': data['business'],
                'cluster': data['cluster'],
                'module': data['module_str'],
                'lan_ip': data['lan_ip'],
                'wan_ip': data['wan_ip'],
                'host_osarch': data['host_osarch'],
                'host_system': data['host_system'],
                'host_kernel': data['host_kernel'],
                'host_cpu_type': data['host_cpu_type'],
                'host_cpu_num': data['host_cpu_num'],
                'host_mem_total': data['host_mem_total']
            }
            data_list.append(temp)
        if not data_list:
            data_list.append({
                'host_name': '',
                'business': '',
                'cluster': '',
                'module': '',
                'lan_ip': '',
                'wan_ip': '',
                'host_osarch': '',
                'host_system': '',
                'host_kernel': '',
                'host_cpu_type': '',
                'host_cpu_num': '',
                'host_mem_total': ''
            })
        params = {
            'file_name': 'HostList',
            'data_list': data_list,
            'headers': ['主机名称', '业务', '集群', '模块', '内网IP', '外网IP', '系统位数', '操作系统', '主机内核', 'CPU类型', 'CPU数量', '内存总量'],
            'data_item': ['host_name', 'business', 'cluster', 'module', 'lan_ip', 'wan_ip', 'host_osarch', 'host_system', 'host_kernel',  'host_cpu_type', 'host_cpu_num', 'host_mem_total'],
            'title': u'主机列表(业务：{0}, 集群：{1}, 模块：{2}, '
                     u'搜索：{3})'.format(business_name, cluster_name,
                                       module_name, search)
        }
        try:
            from export_xls import ExcelExporter
            ee = ExcelExporter(**params)
            file_name = ee()
            file_path = os.path.join(settings.MEDIA_ROOT, "tempfiles", file_name)
            with open(file_path, 'rb') as file_obj:
                data = file_obj.read()
            os.remove(file_path)
            response = HttpResponse(data, content_type='application/vnd.ms-e')
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format('主机列表.xls')
            return response
        except Exception as e:
            print e
            return render(request, 'error_info.html', {"message": "对不起，导出文件失败！", "status_code": 500},
                          status=500)

    @list_route(methods=['POST'])
    @catch_exception_response
    def get_host_ps(self, request):
        """
        获取进行信息
        :param request:
        :return:
        """
        salt_master_obj = models.SaltMaster.objects.first()
        if not salt_master_obj:
            raise Exception('找不到SaltMaster配置信息')

        host_id = request.data.get('host_id', '')
        try:
            salt_minion_obj = models.SaltMinion.objects.get(id=host_id)
        except:
            raise Exception('找不到主机信息')

        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            }

        # 查看新的进程信息
        tasks.get_host_ps_info(salt_master_dict, salt_minion_obj.id)
        return Response('ok')

    @detail_route(methods=['POST'])
    @catch_exception_response
    def change_monitor_ps(self, request, pk):
        monitor_ps = request.data.get('monitor_ps', '')
        host_obj = models.SaltMinion.objects.get(id=pk)
        host_obj.monitor_ps = str(monitor_ps)
        host_obj.save()
        return Response('ok')


class AppInstallViewSet(viewsets.ModelViewSet):
    queryset = models.AppInstall.objects.all()
    serializer_class = serializers.AppInstallSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    search_fields = ('$name', )

    @list_route(methods=['POST'])
    @catch_exception_response
    def minion_install_app(self, request):
        minion_list = request.data.get('minion_list', [])
        app_list = request.data.get('app_list', [])
        salt_master_obj = models.SaltMaster.objects.last()

        if not salt_master_obj:
            raise Exception('没有找到salt服务配置信息！')
        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth}

        # 删除所有app安装状态
        models.AppInstallStatus.objects.all().delete()

        # 启动任务队列，生产任务
        try:
            for salt_minion_id in minion_list:
                # 创建所有app安装状态（等待中）
                for app_install_id in app_list:
                    app_install_status_obj = models.AppInstallStatus(salt_minion_id=salt_minion_id,
                                                                     app_install_id=app_install_id,
                                                                     status='3')
                    app_install_status_obj.save()
                # 启动任务
                tasks.salt_minion_install_app.delay(salt_master_dict, salt_minion_id, app_list)
            return Response('ok')
        except Exception as e:
            print e
            raise Exception('应用安装失败，请检查Celery服务是否开启！')


class AppInstallStatusViewSet(viewsets.ModelViewSet):
    queryset = models.AppInstallStatus.objects.all()
    serializer_class = serializers.AppInstallStatusSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)

    @list_route(methods=['GET'])
    @catch_exception_response
    def delete_all_status(self, request):
        models.AppInstallStatus.objects.all().delete()
        return Response('ok')


class ProjectDeployInfoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    项目部署视图集合，只提供查询接口
    """
    queryset = models.ProjectDeployInfo.objects.all().order_by('step')
    serializer_class = serializers.ProjectDeployInfoSerializer
    filter_backends = (filters.DjangoFilterBackend, GridOrderingFilter)
    filter_class = custom_filters.ProjectDeployInfoFilter


class JenkinsJobsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Jenkins 任务操作API，只提供查询接口
    """
    queryset = models.JenkinsJobs.objects.all()
    serializer_class = serializers.JenkinsJobsSerializer
    filter_backends = (filters.DjangoFilterBackend, GridOrderingFilter)
    filter_class = custom_filters.JenkinsJobsFilter
    pagination_class = CustomPagination

    @list_route(methods=['GET'])
    @catch_exception_response
    def connect_jenkins(self, request):
        jenkins_url = request.GET.get('jenkins_url', '')
        user_id = request.GET.get('user_id', '')
        password = request.GET.get('password', '')
        page = request.GET.get('page', 1)

        try:
            # 实例化jenkins对象，连接远程的jenkins master server
            server = jenkins.Jenkins(jenkins_url, username=user_id, password=password)
            all_jobs = server.get_all_jobs()
        except Exception as e:
            raise Exception('连接Jenkins服务失败，请检查！')

        result_data = []
        for _job in all_jobs:
            job = server.get_job_info(name=_job['name'])
            # job['last_completed_build_info'] = server.get_build_info(job['name'], job['lastCompletedBuild']['number']) if job['lastCompletedBuild'] else ''
            # job['last_successful_build_info'] = server.get_build_info(job['name'], job['lastSuccessfulBuild']['number']) if job['lastSuccessfulBuild'] else ''
            # job['last_unsuccessful_build_info'] = server.get_build_info(job['name'], job['lastUnsuccessfulBuild']['number']) if job['lastUnsuccessfulBuild'] else ''

            result_data.append(job)

        page_result_data = get_page_result(data_list=result_data, page=int(page))
        return Response(page_result_data)

    @list_route(methods=['POST'])
    @catch_exception_response
    def start_build(self, request):
        jenkins_url = request.data.get('jenkins_url', '')
        user_id = request.data.get('user_id', '')
        password = request.data.get('password', '')
        job_name = request.data.get('job_name', [])

        if isinstance(job_name, str):
            job_name_list = [job_name]
        else:
            job_name_list = list(job_name)

        try:
            # 实例化jenkins对象，连接远程的jenkins master server
            server = jenkins.Jenkins(jenkins_url, username=user_id, password=password)
            # 开始构建
            for job_name in job_name_list:
                server.build_job(name=job_name)
        except Exception as e:
            raise Exception('连接Jenkins服务失败，请检查！')

        return Response('ok')

    @list_route(methods=['POST'])
    @catch_exception_response
    def get_build_info(self, request):
        jenkins_url = request.data.get('jenkins_url', '')
        user_id = request.data.get('user_id', '')
        password = request.data.get('password', '')
        job_name = request.data.get('job_name', [])
        jenkins_build_number = request.data.get('jenkins_build_number', 0)

        try:
            # 实例化jenkins对象，连接远程的jenkins master server
            server = jenkins.Jenkins(jenkins_url, username=user_id, password=password)
            # 查询构建信息
            result_data = server.get_build_info(job_name, int(jenkins_build_number))
        except Exception as e:
            raise Exception('连接Jenkins服务失败，请检查！')

        return Response(result_data)

    @list_route(methods=['POST'])
    @catch_exception_response
    def get_build_output(self, request):
        jenkins_url = request.data.get('jenkins_url', '')
        user_id = request.data.get('user_id', '')
        password = request.data.get('password', '')
        job_name = request.data.get('job_name', [])
        jenkins_build_number = request.data.get('jenkins_build_number', 0)

        try:
            # 实例化jenkins对象，连接远程的jenkins master server
            server = jenkins.Jenkins(jenkins_url, username=user_id, password=password)
            # 查询构建信息
            result_data = server.get_build_console_output(job_name, int(jenkins_build_number))
        except Exception as e:
            raise Exception('连接Jenkins服务失败，请检查！')

        return Response(result_data)


class ReceiverHooksViewSet(viewsets.ModelViewSet):
    """
    rancher web hooks 视图结合
    """
    queryset = models.ReceiverHooks.objects.all()
    serializer_class = serializers.ReceiverHooksSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    filter_class = custom_filters.ReceiverHooksFilter
    search_fields = ('$name', '$description')
    pagination_class = CustomPagination

    @list_route(methods=['POST'])
    @catch_exception_response
    def upgrade_app(self, request):
        hooks_id = request.data.get('hooks_id', [])

        if isinstance(hooks_id, int) or isinstance(hooks_id, str):
            hooks_id_list = [hooks_id]
        else:
            hooks_id_list = list(hooks_id)

        result_data = []
        for _id in hooks_id_list:
            try:
                hooks_obj = models.ReceiverHooks.objects.get(pk=_id)
                request_url = hooks_obj.upgrade_url
                post_data = {"push_data": {"tag": hooks_obj.image_label}, "repository": {"repo_name": hooks_obj.image_lib}}
                result = rancher_api.request_receiver_hooks(request_url, post_data)
                if result:
                    hooks_obj.upgrade_time = timezone.now()
                    hooks_obj.save()
                    result_data.append({'name': hooks_obj.name.encode('utf-8'), 'result_status': True, 'result_msg': '升级成功'})
                else:
                    result_data.append({'name': hooks_obj.name.encode('utf-8'), 'result_status': False, 'result_msg': '升级失败，更新地址请求失败！'})
            except:
                result_data.append({'name': '', 'result_status': False, 'result_msg': '找不到应用Hooks的相关信息！'})
        return Response(result_data)

    @list_route(methods=['POST'])
    @catch_exception_response
    def load_rancher_receiver(self, request):
        instances_url = request.data.get('instances_url', '')
        receiver_url = request.data.get('receiver_url', '')
        access_key = request.data.get('access_key', '')
        secret_key = request.data.get('secret_key', '')
        env = request.data.get('env', '')

        # 访问rancher install api（容器列表）
        print instances_url
        print access_key
        print secret_key
        result_data = rancher_api.get_rancher_data(instances_url, access_key, secret_key)
        if result_data:
            if dict(result_data).has_key('resourceType'):
                if result_data['resourceType'] == 'instance':
                    tmp_instance_data = []
                    for data in result_data['data']:
                        tmp_instance_data.append({
                            "image_url": data['imageUuid'].split(":")[1],
                            "labels_list": data['labels'].items()
                        })
                else:
                    raise Exception('导入失败，不是合法的instance api的地址！')
            else:
                raise Exception('导入失败，不是合法的instance api的地址！')
        else:
            raise Exception('导入失败，rancher容器对象API连接失败！')

        # 访问rancher receiver api（接收器列表）
        result_data = rancher_api.get_rancher_data(receiver_url, access_key, secret_key)

        if result_data:
            if dict(result_data).has_key('resourceType'):
                if result_data['resourceType'] == 'receiver':
                    # 删除旧的数据
                    # models.ReceiverHooks.objects.filter(download_receiver=receiver_url).delete()
                    tmp_data_dict = {}
                    for data in result_data['data']:
                        tmp_data_dict['download_receiver'] = receiver_url
                        tmp_data_dict['env'] = env
                        tmp_data_dict['name'] = data['name']
                        tmp_data_dict['upgrade_url'] = data['url']
                        tmp_data_dict['image_label'] = data['serviceUpgradeConfig']['tag']
                        # 获取images地址
                        image_lib_list = []
                        for instances_data in tmp_instance_data:
                            if data['serviceUpgradeConfig']['serviceSelector'].items()[0] in instances_data['labels_list']:
                                image_lib_list.append(instances_data['image_url'])
                        tmp_data_dict['image_lib'] = image_lib_list[0] if len(image_lib_list) > 0 else ''
                        models.ReceiverHooks.objects.update_or_create(**tmp_data_dict)
                else:
                    raise Exception('导入失败，不是合法的receiver api的地址！')
            else:
                raise Exception('导入失败，不是合法的receiver api的地址！')
        else:
            raise Exception('导入失败，rancher接收器API连接失败！')

        return Response('ok')

    @detail_route(methods=['POST'])
    @catch_exception_response
    def backup_image(self, request, pk=None):
        pre_words = request.data.get("pre_words", "")

        try:
            hooks_obj = models.ReceiverHooks.objects.get(id=pk)
        except Exception as e:
            return Exception("找不到相关数据！")

        hooks_obj.push_docker_hub_content += u"%s" % pre_words
        hooks_obj.save()

        try:
            salt_master_obj = models.SaltMaster.objects.last()
        except Exception as e:
            hooks_obj.push_docker_hub_content += u"\n<span class='red'>找不到Salt服务配置！</span>"
            hooks_obj.save()
            return Response({"result_status": False, 'result_message': hooks_obj.push_docker_hub_content})

        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            }
        # 处理目标镜像地址
        if len(hooks_obj.target_docker_hub.split(":")) < 2:
            hooks_obj.target_docker_hub = hooks_obj.target_docker_hub.encode("utf-8") + ":latest"

        # 先做认证，看是否能登录镜像库
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                    username=salt_master_dict["username"],
                                                    password=salt_master_dict["password"],
                                                    eauth=salt_master_dict["eauth"],
                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                    cmd_str="docker login {0} --username {1} --password {2};".format(
                                                        hooks_obj.target_docker_hub,
                                                        hooks_obj.target_docker_hub_username,
                                                        hooks_obj.target_docker_hub_password))
        if _status:
            if "Login Succeeded" not in _data[0][hooks_obj.salt_minion_id]:
                hooks_obj.push_docker_hub_content += u"\n<span class='red'>备份失败，目标镜像仓库连接或认证失败</span>"
                hooks_obj.save()
                return Response(hooks_obj.push_docker_hub_content)
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            hooks_obj.save()
            return Response(hooks_obj.push_docker_hub_content)

        # 能成功登录镜像库
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"], username=salt_master_dict["username"],
                                   password=salt_master_dict["password"], eauth=salt_master_dict["eauth"],
                                   tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                   cmd_str="docker pull {0}".format(hooks_obj.target_docker_hub))

        if _status:
            result_str = _data[0][hooks_obj.salt_minion_id]
            # 目标镜像库镜像成功拉下来了
            if "Digest" in result_str:
                # 更改镜像标签
                target_docker_hub_lib = hooks_obj.target_docker_hub.split(":")[0]
                back_up_label = hooks_obj.target_docker_hub_label if hooks_obj.is_backup and hooks_obj.target_docker_hub_label else datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                            username=salt_master_dict["username"],
                                                            password=salt_master_dict["password"],
                                                            eauth=salt_master_dict["eauth"],
                                                            tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                            cmd_str="docker tag {0} {1}:{2}".format(
                                                                hooks_obj.target_docker_hub,
                                                                target_docker_hub_lib,
                                                                back_up_label
                                                            ))
                if _status:
                    # 上传到镜像库
                    _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                username=salt_master_dict["username"],
                                                                password=salt_master_dict["password"],
                                                                eauth=salt_master_dict["eauth"],
                                                                tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                cmd_str="docker login {0} --username {1} --password {2};docker push {3}:{4}".format(
                                                                    target_docker_hub_lib,
                                                                    hooks_obj.target_docker_hub_username.encode("utf-8"),
                                                                    hooks_obj.target_docker_hub_password.encode("utf-8"),
                                                                    target_docker_hub_lib,
                                                                    back_up_label,
                                                                ))
                    if _status:
                        if 'digest' in _data[0][hooks_obj.salt_minion_id]:
                            # 删除旧的镜像
                            saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                       username=salt_master_dict["username"],
                                                       password=salt_master_dict["password"],
                                                       eauth=salt_master_dict["eauth"],
                                                       tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                       cmd_str="docker rmi -f {0}; docker rmi -f {1}:{2}".format(
                                                           hooks_obj.target_docker_hub.encode("utf-8"),
                                                           target_docker_hub_lib,
                                                           back_up_label,
                                                       ))
                            hooks_obj.push_docker_hub_content += u"\n备份成功，备份镜像为：%s:%s" % (unicode(target_docker_hub_lib), unicode(back_up_label))
                        else:
                            hooks_obj.push_docker_hub_content += u"\n<span class='red'>备份失败，目标镜像仓库认证失败</span>"
                    else:
                        hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                else:
                    hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            # 目标镜像库没有这个镜像
            else:
                hooks_obj.push_docker_hub_content += u"\n备份没有进行，因为目标镜像库地址中不存在这个镜像！"
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)

        hooks_obj.save()
        return Response(hooks_obj.push_docker_hub_content)

    @detail_route(methods=['POST'])
    # @catch_exception_response
    def push_image(self, request, pk=None):
        pre_words = request.data.get("pre_words", "")

        try:
            hooks_obj = models.ReceiverHooks.objects.get(id=pk)
        except Exception as e:
            return Exception("找不到相关数据！")

        hooks_obj.push_docker_hub_content += u"%s" % pre_words
        hooks_obj.save()

        try:
            salt_master_obj = models.SaltMaster.objects.last()
        except Exception as e:
            hooks_obj.push_docker_hub_content += u"\n<span class='red'>找不到Salt服务配置！</span>"
            hooks_obj.save()
            return Response({"result_status": False, 'result_message': hooks_obj.push_docker_hub_content})

        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            }
        # 处理目标镜像地址
        if len(hooks_obj.target_docker_hub.split(":")) < 2:
            hooks_obj.target_docker_hub = hooks_obj.target_docker_hub.encode("utf-8") + ":latest"

        # 先做认证，看是否能登录镜像库
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                    username=salt_master_dict["username"],
                                                    password=salt_master_dict["password"],
                                                    eauth=salt_master_dict["eauth"],
                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                    cmd_str="docker login {0} --username {1} --password {2};".format(
                                                        hooks_obj.target_docker_hub,
                                                        hooks_obj.target_docker_hub_username,
                                                        hooks_obj.target_docker_hub_password))
        if _status:
            if "Login Succeeded" not in _data[0][hooks_obj.salt_minion_id]:
                hooks_obj.push_docker_hub_content += u"\n<span class='red'>发布失败，目标镜像仓库连接或认证失败</span>"
                hooks_obj.save()
                return Response(hooks_obj.push_docker_hub_content)
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            hooks_obj.save()
            return Response(hooks_obj.push_docker_hub_content)

        # 能成功登录镜像库
        # 拉取源镜像
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                    username=salt_master_dict["username"],
                                                    password=salt_master_dict["password"],
                                                    eauth=salt_master_dict["eauth"],
                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                    cmd_str="docker pull {0}:{1}".format(hooks_obj.image_lib.encode('utf-8'),
                                                                                         hooks_obj.image_label).encode('utf-8'))

        if _status:
            result_str = _data[0][hooks_obj.salt_minion_id]
            # 源镜像库镜像成功拉下来了
            if "Digest" in result_str:
                # 更改镜像标签
                _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                            username=salt_master_dict["username"],
                                                            password=salt_master_dict["password"],
                                                            eauth=salt_master_dict["eauth"],
                                                            tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                            cmd_str="docker tag {0}:{1} {2}".format(
                                                                hooks_obj.image_lib.encode(
                                                                        "utf-8"),
                                                                hooks_obj.image_label.encode(
                                                                        "utf-8"),
                                                                hooks_obj.target_docker_hub.encode(
                                                                        "utf-8"),
                                                            ))
                if _status:
                    # 上传到镜像库
                    _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                username=salt_master_dict["username"],
                                                                password=salt_master_dict["password"],
                                                                eauth=salt_master_dict["eauth"],
                                                                tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                cmd_str="docker login {0} --username {1} --password {2};docker push {0}".format(
                                                                    hooks_obj.target_docker_hub.encode(
                                                                        "utf-8"),
                                                                    hooks_obj.target_docker_hub_username.encode(
                                                                        "utf-8"),
                                                                    hooks_obj.target_docker_hub_password.encode(
                                                                        "utf-8"),
                                                                ))
                    if _status:
                        if 'digest' in _data[0][hooks_obj.salt_minion_id]:
                            # 删除旧的镜像
                            saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                       username=salt_master_dict["username"],
                                                       password=salt_master_dict["password"],
                                                       eauth=salt_master_dict["eauth"],
                                                       tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                       cmd_str="docker rmi -f {0}; docker rmi -f {1}:{2}".format(
                                                           hooks_obj.target_docker_hub.encode("utf-8"),
                                                           hooks_obj.image_lib.encode("utf-8"),
                                                           hooks_obj.image_label.encode("utf-8"),
                                                       ))
                            hooks_obj.push_docker_hub_content += u"\n发布成功，新的镜像为：%s" % unicode(hooks_obj.target_docker_hub)
                        else:
                            hooks_obj.push_docker_hub_content += u"\n<span class='red'>发布失败，目标镜像仓库认证失败</span>"
                    else:
                        hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                else:
                    hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            # 目标镜像库没有这个镜像
            else:
                hooks_obj.push_docker_hub_content += u"\n发布没有进行，拉取源镜像失败！"
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)

        hooks_obj.save()
        return Response(hooks_obj.push_docker_hub_content)

    @detail_route(methods=['POST'])
    @catch_exception_response
    def backup_image_local(self, request, pk=None):
        pre_words = request.data.get("pre_words", "")

        try:
            hooks_obj = models.ReceiverHooks.objects.get(id=pk)
        except Exception as e:
            return Exception("找不到相关数据！")

        hooks_obj.push_docker_hub_content += u"%s" % pre_words
        hooks_obj.save()

        try:
            salt_master_obj = models.SaltMaster.objects.last()
        except Exception as e:
            hooks_obj.push_docker_hub_content += u"\n<span class='red'>找不到Salt服务配置！</span>"
            hooks_obj.save()
            return Response({"result_status": False, 'result_message': hooks_obj.push_docker_hub_content})

        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            }
        # 处理应用镜像地址
        local_docker_hub_url = hooks_obj.load_docker_hub
        if len(local_docker_hub_url.split(":")) < 2:
            local_docker_hub_url = local_docker_hub_url.encode("utf-8") + ":latest"

        # 先做认证，看是否能登录镜像库
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                    username=salt_master_dict["username"],
                                                    password=salt_master_dict["password"],
                                                    eauth=salt_master_dict["eauth"],
                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                    cmd_str="docker login {0} --username {1} --password {2};".format(
                                                        local_docker_hub_url,
                                                        hooks_obj.target_docker_hub_username,
                                                        hooks_obj.target_docker_hub_password))

        if _status:
            if "Login Succeeded" not in _data[0][hooks_obj.salt_minion_id]:
                hooks_obj.push_docker_hub_content += u"\n<span class='red'>备份失败，镜像仓库连接或认证失败</span>"
                hooks_obj.save()
                return Response(hooks_obj.push_docker_hub_content)
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            hooks_obj.save()
            return Response(hooks_obj.push_docker_hub_content)

        # 能成功登录镜像库
        try:
            _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                        username=salt_master_dict["username"],
                                                        password=salt_master_dict["password"],
                                                        eauth=salt_master_dict["eauth"],
                                                        tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                        cmd_str="docker pull {0}".format(local_docker_hub_url))

            if _status:
                result_str = _data[0][hooks_obj.salt_minion_id]
                # 目标镜像库镜像成功拉下来了
                if "Digest" in result_str:
                    # 更改镜像标签
                    local_docker_hub_lib = hooks_obj.image_lib
                    back_up_label = hooks_obj.target_docker_hub_label if hooks_obj.is_backup and hooks_obj.target_docker_hub_label else "backup"
                    _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                username=salt_master_dict["username"],
                                                                password=salt_master_dict["password"],
                                                                eauth=salt_master_dict["eauth"],
                                                                tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                cmd_str="docker tag {0} {1}:{2}".format(
                                                                    local_docker_hub_url,
                                                                    local_docker_hub_lib,
                                                                    back_up_label
                                                                ))
                    if _status:
                        # 上传到镜像库
                        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                    username=salt_master_dict["username"],
                                                                    password=salt_master_dict["password"],
                                                                    eauth=salt_master_dict["eauth"],
                                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                    cmd_str="docker login {0} --username {1} --password {2};docker push {3}:{4}".format(
                                                                        local_docker_hub_url,
                                                                        hooks_obj.target_docker_hub_username.encode(
                                                                            "utf-8"),
                                                                        hooks_obj.target_docker_hub_password.encode(
                                                                            "utf-8"),
                                                                        local_docker_hub_lib,
                                                                        back_up_label,
                                                                    ))
                        if _status:
                            if 'digest' in _data[0][hooks_obj.salt_minion_id]:
                                # 删除旧的镜像
                                saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                           username=salt_master_dict["username"],
                                                           password=salt_master_dict["password"],
                                                           eauth=salt_master_dict["eauth"],
                                                           tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                           cmd_str="docker rmi -f {0}; docker rmi -f {1}:{2}".format(
                                                               local_docker_hub_url,
                                                               local_docker_hub_lib,
                                                               back_up_label,
                                                           ))
                                hooks_obj.push_docker_hub_content += u"\n备份成功，备份镜像为：%s:%s" % (
                                unicode(local_docker_hub_lib), unicode(back_up_label))
                            else:
                                hooks_obj.push_docker_hub_content += u"\n<span class='red'>备份失败，镜像仓库认证失败</span>"
                        else:
                            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                    else:
                        hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                # 目标镜像库没有这个镜像
                else:
                    hooks_obj.push_docker_hub_content += u"\n备份没有进行，因为镜像库地址中不存在这个镜像！"
            else:
                hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
        except:
            hooks_obj.push_docker_hub_content += u"\n%s" % u"<span class='red'>备份失败，拉取镜像失败</span>"

        hooks_obj.save()
        return Response(hooks_obj.push_docker_hub_content)

    @detail_route(methods=['POST'])
    @catch_exception_response
    def pull_image(self, request, pk=None):
        pre_words = request.data.get("pre_words", "")

        try:
            hooks_obj = models.ReceiverHooks.objects.get(id=pk)
        except Exception as e:
            return Exception("找不到相关数据！")

        hooks_obj.push_docker_hub_content += u"%s" % pre_words
        hooks_obj.save()

        try:
            salt_master_obj = models.SaltMaster.objects.last()
        except Exception as e:
            hooks_obj.push_docker_hub_content += u"\n<span class='red'>找不到Salt服务配置！</span>"
            hooks_obj.save()
            return Response({"result_status": False, 'result_message': hooks_obj.push_docker_hub_content})

        salt_master_dict = {"api_url": salt_master_obj.api_url, "username": salt_master_obj.username,
                            "password": str(aes_html_data_decrypt(str(salt_master_obj.password)))
                            if salt_master_obj.password else '', "eauth": salt_master_obj.eauth,
                            }
        # 处理应用镜像地址
        local_docker_hub_url = hooks_obj.load_docker_hub
        if len(local_docker_hub_url.split(":")) < 2:
            local_docker_hub_url = local_docker_hub_url.encode("utf-8") + ":latest"

        # 处理源镜像地址
        if len(hooks_obj.target_docker_hub.split(":")) < 2:
            hooks_obj.target_docker_hub = hooks_obj.target_docker_hub.encode("utf-8") + ":latest"

        # 先做认证，看是否能登录镜像库
        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                    username=salt_master_dict["username"],
                                                    password=salt_master_dict["password"],
                                                    eauth=salt_master_dict["eauth"],
                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                    cmd_str="docker login {0} --username {1} --password {2};".format(
                                                        local_docker_hub_url,
                                                        hooks_obj.target_docker_hub_username,
                                                        hooks_obj.target_docker_hub_password))
        if _status:
            if "Login Succeeded" not in _data[0][hooks_obj.salt_minion_id]:
                hooks_obj.push_docker_hub_content += u"\n<span class='red'>导入失败，镜像仓库连接或认证失败</span>"
                hooks_obj.save()
                return Response(hooks_obj.push_docker_hub_content)
        else:
            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
            hooks_obj.save()
            return Response(hooks_obj.push_docker_hub_content)

        # 能成功登录镜像库
        # 拉取源镜像
        try:
            _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                        username=salt_master_dict["username"],
                                                        password=salt_master_dict["password"],
                                                        eauth=salt_master_dict["eauth"],
                                                        tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                        cmd_str="docker pull {0}".format(
                                                            hooks_obj.target_docker_hub.encode('utf-8')))

            if _status:
                result_str = _data[0][hooks_obj.salt_minion_id]
                # 源镜像库镜像成功拉下来了
                if "Digest" in result_str:
                    # 更改镜像标签
                    _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                username=salt_master_dict["username"],
                                                                password=salt_master_dict["password"],
                                                                eauth=salt_master_dict["eauth"],
                                                                tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                cmd_str="docker tag {0} {1}".format(
                                                                    hooks_obj.target_docker_hub.encode('utf-8'),
                                                                    local_docker_hub_url
                                                                ))
                    if _status:
                        # 上传到镜像库
                        _status, _data = saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                                    username=salt_master_dict["username"],
                                                                    password=salt_master_dict["password"],
                                                                    eauth=salt_master_dict["eauth"],
                                                                    tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                                    cmd_str="docker login {0} --username {1} --password {2};docker push {0}".format(
                                                                        local_docker_hub_url,
                                                                        hooks_obj.target_docker_hub_username.encode(
                                                                            "utf-8"),
                                                                        hooks_obj.target_docker_hub_password.encode(
                                                                            "utf-8"),
                                                                    ))
                        if _status:
                            if 'digest' in _data[0][hooks_obj.salt_minion_id]:
                                # 删除旧的镜像
                                saltapi_manager.minion_run(request_url=salt_master_dict["api_url"],
                                                           username=salt_master_dict["username"],
                                                           password=salt_master_dict["password"],
                                                           eauth=salt_master_dict["eauth"],
                                                           tgt_id=hooks_obj.salt_minion_id, fun="cmd.run",
                                                           cmd_str="docker rmi -f {0}; docker rmi -f {1}".format(
                                                               local_docker_hub_url,
                                                               hooks_obj.target_docker_hub.encode('utf-8'),
                                                           ))
                                hooks_obj.push_docker_hub_content += u"\n导入成功，新的镜像为：%s" % unicode(
                                    local_docker_hub_url)
                            else:
                                hooks_obj.push_docker_hub_content += u"\n<span class='red'>导入失败，镜像仓库认证失败</span>"
                        else:
                            hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                    else:
                        hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
                # 目标镜像库没有这个镜像
                else:
                    hooks_obj.push_docker_hub_content += u"\n<span class='red'>导入失败，拉取源镜像失败！</span>"
            else:
                hooks_obj.push_docker_hub_content += u"\n%s" % unicode(_data)
        except:
            hooks_obj.push_docker_hub_content += u"\n%s" % u"<span class='red'>导入失败，拉取源镜像失败</span>"

        hooks_obj.save()
        return Response(hooks_obj.push_docker_hub_content)