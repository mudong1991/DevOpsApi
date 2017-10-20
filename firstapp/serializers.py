# -*- coding:utf-8 -*-
# file: serializers
# author: Mundy
# date: 2017/5/4 0004
"""
序列化类
"""
import json
from rest_framework import serializers
from custom_validators import *
from urlparse import urlparse
from django.conf import settings
from firstapp import models
from firstapp.util_aes import aes_api_data_encrypt, aes_html_data_decrypt
from firstapp import cust_exceptions
from salt_api import saltapi_manager


def get_error_messages(label):
    return {
        "blank": "{0}: 不能为空！".format(label),
        "unique": "{0}: 已经存在！".format(label),
        "max_length": "{0}:长度超过指定范围！".format(label),
        "invalid": "{0}: 填写合法的整数值".format(label)
    }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class BusinessAdminSerializer(serializers.ModelSerializer):
    """
    业务管理模型数据序列化
    """
    host_num = serializers.SerializerMethodField(method_name='get_host_count')
    create_time = serializers.DateTimeField(format=settings.TIME_FORMAT, required=False)

    def get_host_count(self, obj):
        """
        获取当前业务下面的主机个数
        :param obj:
        :return:
        """
        all_modules = obj.modules.all()
        host_list = []
        for module in all_modules:
            host_list += module.salt_minions.all()
        host_unique_list = set([host.id for host in host_list])
        return len(host_unique_list)

    class Meta:
        model = models.BusinessAdmin
        fields = '__all__'


class ClusterSerializer(serializers.ModelSerializer):

    # 添加和修改数据的唯一性判断
    def create(self, validated_data):
        if models.Cluster.objects.filter(business=validated_data['business'], name=validated_data['name']).exists():
            raise cust_exceptions.ValidationFailed(detail="对不起，该业务下已存在该名称的集群！")
        return super(ClusterSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if models.Cluster.objects.exclude(id=instance.id).filter(business=validated_data['business'], name=validated_data['name']).exists():
            raise cust_exceptions.ValidationFailed(detail="对不起，该业务下已存在该名称的集群！")
        return super(ClusterSerializer, self).update(instance, validated_data)

    class Meta:
        model = models.Cluster
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    cluster__name = serializers.CharField(source='cluster.name', read_only=True)

    # 添加和修改数据的唯一性判断
    def create(self, validated_data):
        # 三级拓扑
        if int(validated_data['business'].topology) == 1 and validated_data['cluster']:
            if models.Module.objects.filter(business=validated_data['business'], cluster=validated_data['cluster'], name=validated_data['name']).exists():
                raise cust_exceptions.ValidationFailed(detail="对不起，该集群下已存在该名称的集群！")
        # 二级拓扑
        else:
            if models.Module.objects.filter(business=validated_data['business'], name=validated_data['name']).exists():
                raise cust_exceptions.ValidationFailed(detail="对不起，该业务下已存在该名称的集群！")

        return super(ModuleSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # 三级拓扑
        if int(validated_data['business'].topology) == 1 and validated_data['cluster']:
            if models.Module.objects.exclude(id=instance.id).filter(business=validated_data['business'], cluster=validated_data['cluster'],
                                            name=validated_data['name']).exists():
                raise cust_exceptions.ValidationFailed(detail="对不起，该集群下已存在该名称的集群！")
        # 二级拓扑
        else:
            if models.Module.objects.exclude(id=instance.id).filter(business=validated_data['business'], name=validated_data['name']).exists():
                raise cust_exceptions.ValidationFailed(detail="对不起，该业务下已存在该名称的集群！")

        return super(ModuleSerializer, self).update(instance, validated_data)

    class Meta:
        model = models.Module
        fields = '__all__'


class ProjectCenterSerializer(serializers.ModelSerializer):
    deploy_time = serializers.DateTimeField(format=settings.TIME_FORMAT, required=False, allow_null=True)
    deploy_docker_info = serializers.SerializerMethodField(method_name='get_docker_info', required=False, allow_null=True)
    deploy_status = serializers.SerializerMethodField(method_name='format_deploy_status',  required=False, allow_null=True)

    def format_deploy_status(self, obj):
        project_id = obj.id
        project_docker_list = models.ProjectDockerInfo.objects.filter(project_id=project_id)
        if project_docker_list:
            # 全部状态是等待任务中
            if False not in [project_docker.status == '0' for project_docker in project_docker_list]:
                return '0'
            else:
                # 有一个任务已经开始
                if True in [project_docker.status == '1' for project_docker in project_docker_list]:
                    return '1'
                else:
                    # 有任务失败
                    if True in [(project_docker.status == '3') for project_docker in project_docker_list]:
                        return '3'
                    # 全部成功
                    else:
                        return '2'
        else:
            return ''

    def create(self, validated_data):
        try:
            repo_url_split = urlparse(validated_data['lib_url'])
            # 项目名称
            project_word_list = repo_url_split.path.split("/")[-1].split(".")[:-1]
            project_name = '.'.join(project_word_list)
        except:
            raise cust_exceptions.ValidationFailed(detail="仓库地址不规范！")
        project_path = '/' + project_name
        if validated_data.has_key('lib_path'):
            if validated_data['lib_path']:
                project_path = project_path + '/' + validated_data['lib_path']
        if validated_data.has_key('lib_deploy_path'):
            deploy_container_name = validated_data['lib_deploy_path'] if validated_data['lib_deploy_path'] else project_path.split("/")[-1]
        else:
            deploy_container_name = project_path.split("/")[-1]
        validated_data['deploy_container_name'] = deploy_container_name
        if validated_data['deploy_container_name']:
            if validated_data.has_key('version'):
                if validated_data['version']:
                    validated_data['docker_img_name'] = deploy_container_name + (':%s' % validated_data['version'])
                else:
                    validated_data['docker_img_name'] = deploy_container_name + ':latest'
            else:
                validated_data['docker_img_name'] = deploy_container_name + ':latest'
        else:
            validated_data['docker_img_name'] = ''
        validated_data['deploy_docker_run'] = "docker run --name {0} --net=host -d {1}"\
            .format(validated_data['deploy_container_name'], validated_data['docker_img_name'])
        return super(ProjectCenterSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        try:
            repo_url_split = urlparse(validated_data['lib_url'])
            # 项目名称
            project_word_list = repo_url_split.path.split("/")[-1].split(".")[:-1]
            project_name = '.'.join(project_word_list)
        except:
            raise cust_exceptions.ValidationFailed(detail="仓库地址不规范！")
        project_path = '/' + project_name
        if validated_data.has_key('lib_path'):
            if validated_data['lib_path']:
                project_path = project_path + '/' + validated_data['lib_path']
        if validated_data.has_key('lib_deploy_path'):
            deploy_container_name = validated_data['lib_deploy_path'] if validated_data['lib_deploy_path'] else project_path.split("/")[-1]
        else:
            deploy_container_name = project_path.split("/")[-1]
        validated_data['deploy_container_name'] = deploy_container_name
        if validated_data['deploy_container_name']:
            if validated_data.has_key('version'):
                if validated_data['version']:
                    validated_data['docker_img_name'] = deploy_container_name + (':%s' % validated_data['version'])
                else:
                    validated_data['docker_img_name'] = deploy_container_name + ':latest'
            else:
                validated_data['docker_img_name'] = deploy_container_name + ':latest'
        else:
            validated_data['docker_img_name'] = ''
        validated_data['deploy_docker_run'] = "docker run --name {0} --net=host -d {1}" \
            .format(validated_data['deploy_container_name'], validated_data['docker_img_name'])
        return super(ProjectCenterSerializer, self).update(instance, validated_data)

    def get_docker_info(self, obj):
        project_id = obj.id
        project_docker_obj_list = models.ProjectDockerInfo.objects.filter(project_id=project_id)
        result_data = []
        for project_docker_obj in project_docker_obj_list:
            result_data.append({
                'salt_minion_id': project_docker_obj.salt_minion.minion_id,
                'port': project_docker_obj.port,
                'progress': project_docker_obj.progress,
                'status': project_docker_obj.status,
                'message': project_docker_obj.message
            })
        return result_data

    class Meta:
        model = models.ProjectCenter
        fields = '__all__'


class ProjectDockerInfoSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name',  read_only=True, required=False)
    minion_id = serializers.CharField(source='salt_minion.minion_id', read_only=True, required=False)
    generated_time = serializers.DateTimeField(format=settings.TIME_FORMAT, required=False, allow_null=True)
    deploy_step_title = serializers.SerializerMethodField(method_name='get_step_title', read_only=True, required=False,
                                                          allow_null=True)

    def get_step_title(self, obj):
        last_deploy_step = models.ProjectDeployInfo.objects.filter(project_docker=obj).last()
        if last_deploy_step:
            return last_deploy_step.title
        else:
            return ''

    class Meta:
        model = models.ProjectDockerInfo
        fields = '__all__'


class SaltMasterSerializer(serializers.ModelSerializer):
    """
    salt master序列化
    """
    def create(self, validated_data):
        # 获取token
        request_url = validated_data['api_url'] if validated_data.has_key('api_url') else ''
        username = validated_data['username'] if validated_data.has_key('username') else ''
        password = validated_data['password'] if validated_data.has_key('password') else ''
        eauth = validated_data['eauth'] if validated_data.has_key('eauth') else ''

        status, data = saltapi_manager.login_salt(request_url, username, password, eauth)
        token = data if status else None

        validated_data['token'] = token
        # 密码加密
        if validated_data.has_key('password'):
            validated_data['password'] = aes_api_data_encrypt(str(validated_data['password']))
        return super(SaltMasterSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # 先解密获取token
        if validated_data['password'] == instance.password:
            validated_data['password'] = str(aes_html_data_decrypt(str(validated_data['password'])))

        # 获取token
        request_url = validated_data['api_url'] if validated_data.has_key('api_url') else ''
        username = validated_data['username'] if validated_data.has_key('username') else ''
        password = validated_data['password'] if validated_data.has_key('password') else ''
        eauth = validated_data['eauth'] if validated_data.has_key('eauth') else ''

        status, data = saltapi_manager.login_salt(request_url, username, password, eauth)
        token = data if status else None

        validated_data['token'] = token

        # 密码加密
        if validated_data.has_key('password'):
            validated_data['password'] = aes_api_data_encrypt(str(validated_data['password']))
        return super(SaltMasterSerializer, self).update(instance, validated_data)

    class Meta:
        model = models.SaltMaster
        fields = '__all__'


class SaltMinionSerializer(serializers.ModelSerializer):
    salt_master_name = serializers.CharField(source='salt_master.name', read_only=True, required=False)
    module_str = serializers.SerializerMethodField(method_name='get_module_string', read_only=True)
    business = serializers.SerializerMethodField(method_name='get_host_business', read_only=True, required=False)
    cluster = serializers.SerializerMethodField(method_name='get_host_cluster', read_only=True, required=False)

    def get_module_string(self, obj):
        module_list = list(set([m.name for m in obj.module.all()]))
        return ','.join(module_list)

    def get_host_business(self, obj):
        business_list = list(set([m.business.name for m in obj.module.all() if m.business]))
        return ','.join(business_list)

    def get_host_cluster(self, obj):
        cluster_list = list(set([m.cluster.name for m in obj.module.all() if m.cluster]))
        return ','.join(cluster_list)

    class Meta:
        model = models.SaltMinion
        fields = '__all__'


class AppInstallSerializer(serializers.ModelSerializer):
    app_image_str = serializers.CharField(source='app_image', read_only=True, required=False)

    class Meta:
        model = models.AppInstall
        fields = '__all__'


class AppInstallStatusSerializer(serializers.ModelSerializer):
    salt_minion = serializers.CharField(source='salt_minion.minion_id', read_only=True, required=False)
    app_version = serializers.CharField(source='app_install.version', read_only=True, required=False)
    app_name = serializers.CharField(source='app_install.name', read_only=True, required=False)

    class Meta:
        model = models.AppInstallStatus
        fields = '__all__'


class ProjectDeployInfoSerializer(serializers.ModelSerializer):
    """
    项目部署序列化类
    """
    class Meta:
        model = models.ProjectDeployInfo
        fields = '__all__'


class JenkinsJobsSerializer(serializers.ModelSerializer):
    """
    Jenkins按任务序列化类
    """
    last_completed_build = serializers.SerializerMethodField(method_name='format_last_completed_build', required=False,
                                                             read_only=True)
    last_successful_build = serializers.SerializerMethodField(method_name='format_last_successful_build', required=False,
                                                             read_only=True)
    last_unsuccessful_build = serializers.SerializerMethodField(method_name='format_last_unsuccessful_build', required=False,
                                                             read_only=True)
    last_completed_build_info = serializers.SerializerMethodField(method_name='format_last_completed_build_info', required=False,
                                                             read_only=True)
    last_successful_build_info = serializers.SerializerMethodField(method_name='format_last_successful_build_info',
                                                              required=False,
                                                              read_only=True)
    last_unsuccessful_build_info = serializers.SerializerMethodField(method_name='format_last_unsuccessful_build_info',
                                                                required=False,
                                                                read_only=True)

    def format_last_completed_build(self, obj):
        if obj.last_completed_build:
            return eval(str(obj.last_completed_build))
        else:
            return ''

    def format_last_successful_build(self, obj):
        if obj.last_successful_build:
            return eval(str(obj.last_successful_build))
        else:
            return ''

    def format_last_unsuccessful_build(self, obj):
        if obj.last_unsuccessful_build_info:
            return eval(str(obj.last_unsuccessful_build))
        else:
            return ''

    def format_last_completed_build_info(self, obj):
        if obj.last_completed_build_info:
            return eval(str(obj.last_completed_build_info))
        else:
            return ''

    def format_last_successful_build_info(self, obj):
        if obj.last_successful_build_info:
            return eval(str(obj.last_successful_build_info))
        else:
            return ''

    def format_last_unsuccessful_build_info(self, obj):
        if obj.last_unsuccessful_build_info:
            return eval(str(obj.last_unsuccessful_build_info))
        else:
            return ''

    class Meta:
        model = models.JenkinsJobs
        fields = '__all__'


class ReceiverHooksSerializer(serializers.ModelSerializer):
    """
    rancher receiver hooks
    """
    upgrade_time = serializers.DateTimeField(format=settings.TIME_FORMAT, required=False, allow_null=True)
    push_docker_hub_time = serializers.DateTimeField(format=settings.TIME_FORMAT, required=False, allow_null=True)

    class Meta:
        model = models.ReceiverHooks
        fields = '__all__'
