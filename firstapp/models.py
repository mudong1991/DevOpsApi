# -*- coding:utf-8 -*-
# Created by mudong at 2017/3/8 0008
from django.db import models
from django.utils import timezone


# Create your models here.
def get_error_messages(label):
    return {
        "blank": "{0}: 不能为空！".format(label),
        "unique": "{0}: 已经存在！".format(label),
        "max_length": "{0}:长度超过指定范围！".format(label),
        "invalid": "{0}: 填写合法的整数值".format(label)
    }


class BusinessAdmin(models.Model):
    """
    业务管理
    """
    topology_type = (
        (0, u'二级拓扑'),
        (1, u'三级拓扑')
    )
    lifecycle_type = (
        (0, u'停运'),
        (1, u'测试'),
        (2, u'运营')
    )

    topology = models.IntegerField(choices=topology_type, help_text='拓扑结构（0-二级拓扑， 1-三级拓扑）')
    name = models.CharField(max_length=255, help_text='业务名称', unique=True, error_messages=get_error_messages('业务名称'))
    create_user = models.CharField(max_length=255, blank=True, null=True, help_text='创建人员')
    create_time = models.DateTimeField(default=timezone.now, blank=True, null=True, help_text='创建时间')
    lifecycle = models.IntegerField(default=1, blank=True, null=True, choices=lifecycle_type, help_text="生命周期（0-停运，1-测试， 2-运营）")
    product_user = models.CharField(max_length=255, blank=True, null=True, help_text='产品人员')
    develop_user = models.CharField(max_length=255, blank=True, null=True, help_text='开发人员')
    operation_user = models.CharField(max_length=255, blank=True, null=True, help_text='运维人员')
    test_user = models.CharField(max_length=255, blank=True, null=True, help_text='测试人员')

    class Meta:
        db_table = 'business_admin'


class Cluster(models.Model):
    """
    业务集群信息
    """
    env_type_options = (
        (0, u'测试'),
        (1, u'体验'),
        (2, u'正式'),
    )
    business = models.ForeignKey(BusinessAdmin, related_name='clusters', help_text='业务')
    name = models.CharField(max_length=100, help_text='集群名字')
    env_type = models.IntegerField(default=0, choices=env_type_options, help_text='环境类型')
    service_status = models.BooleanField(default=True, help_text='服务状态')
    cn_name = models.CharField(max_length=100, blank=True, null=True, help_text='中文名字')
    description = models.CharField(max_length=500, null=True, blank=True, help_text='描述')

    class Meta:
        db_table = 'cluster'


class Module(models.Model):
    """
    集群下的模块
    """
    module_type_options = (
        (0, '故障机'),
        (1, '空闲机'),
        (2, '业务模块')
    )
    business = models.ForeignKey(BusinessAdmin, related_name='modules', help_text='业务')
    cluster = models.ForeignKey(Cluster, blank=True, null=True, related_name='modules', help_text='集群')
    name = models.CharField(max_length=100, help_text='模块名字')
    maintain_user = models.CharField(max_length=255, blank=True, null=True, help_text='维护人')
    description = models.CharField(max_length=500, blank=True, null=True, help_text='描述')

    class Meta:
        db_table = 'module'


class SaltMaster(models.Model):
    """
    salt服务端
    """
    name = models.CharField(max_length=200, help_text='名称', unique=True, error_messages=get_error_messages('名称'))
    api_url = models.CharField(max_length=500, blank=False, null=False, help_text='salt-api url地址')
    username = models.CharField(max_length=200, blank=True, null=True, help_text='用户名')
    password = models.CharField(max_length=200, blank=True, null=True, help_text='密码')
    eauth = models.CharField(max_length=200, blank=True, null=True, help_text='用户组')
    self_minion_id = models.CharField(max_length=200, blank=True, null=True, help_text='本身作为minion的id')
    token = models.CharField(max_length=300, blank=True, null=True, help_text='登录成功后获取的token')
    description = models.CharField(max_length=500, blank=True, null=True, help_text='备注')

    class Meta:
        db_table = 'salt_master'


class SaltMinion(models.Model):
    salt_master = models.ForeignKey(SaltMaster, blank=True, null=True, help_text='salt-master服务端')
    module = models.ManyToManyField(Module, blank=True, help_text='所属模块', related_name='salt_minions')
    online = models.NullBooleanField(default=True, blank=True, null=True, help_text='在线状态')
    monitor_ps = models.CharField(max_length=10, default='0', blank=True, null=True, help_text='是否监控进程(0-关，1-开)')
    # 主机信息
    # salt-info
    minion_id = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text='minion客户端id')
    # 基础信息
    host_name = models.CharField(max_length=500, blank=True, null=True, help_text='主机名')
    host_osarch = models.CharField(max_length=100, blank=True, null=True, help_text='系统位数')
    host_system = models.CharField(max_length=500, blank=True, null=True, help_text='操作系统')
    host_kernel = models.CharField(max_length=500, blank=True, null=True, help_text='主机内核')
    # CPU信息
    host_cpu_type = models.CharField(max_length=500, blank=True, null=True, help_text='CPU类型')
    host_cpu_num = models.IntegerField(blank=True, null=True, help_text='CPU数量')
    # 网络
    lan_ip = models.GenericIPAddressField(blank=True, null=True, help_text='内网ip')
    wan_ip = models.GenericIPAddressField(blank=True, null=True, help_text='外网ip')
    # 内存信息
    host_mem_total = models.IntegerField(blank=True, null=True, help_text='内存总量')

    class Meta:
        db_table = 'salt_minion'


class ProjectCenter(models.Model):
    develop_type_options = (
        ('0', 'java'),
        ('1', 'python'),
        ('2', 'node.js'),
    )
    code_lib_type_options = (
        ('0', 'Git'),
        ('1', 'SVN')
    )
    status_options = (
        ('0', '等待中'),
        ('1', '任务进行中'),
        ('2', '任务完成'),
        ('3', '部署有任务失败'),
    )

    # 基本信息
    name = models.CharField(max_length=255, unique=True, error_messages=get_error_messages('项目名称'), help_text='项目名称')
    version = models.CharField(max_length=100, blank=True, null=True, help_text='版本')
    description = models.CharField(max_length=500, blank=True, null=True, help_text='项目简介')
    head = models.CharField(max_length=255, blank=True, null=True, help_text='负责人')
    # 仓库地址信息
    code_lib_type = models.CharField(max_length=10, default='0', choices=code_lib_type_options, help_text='代码仓库')
    lib_url = models.CharField(max_length=500, help_text='代码库地址')
    lib_branch = models.CharField(max_length=200, blank=True, null=True, help_text='分支名')
    lib_path = models.CharField(max_length=300, blank=True, null=True, help_text='项目所在仓库路径（绝对路径）')
    lib_deploy_path = models.CharField(max_length=300, blank=True, null=True, help_text='项目中需要部署路径（相对lib_path路径）')
    lib_username = models.CharField(max_length=255, blank=True, null=True, help_text='代码库账户')
    lib_password = models.CharField(max_length=255, blank=True, null=True, help_text='代码库密码')
    develop_type = models.CharField(max_length=20, default='0', choices=develop_type_options, help_text='开发语言')
    # 部署信息
    deploy_time = models.DateTimeField(blank=True, null=True, help_text='部署时间')
    deploy_status = models.CharField(max_length=100, blank=True, null=True, choices=status_options, help_text='状态')
    deploy_salt_minion = models.ManyToManyField(SaltMinion, blank=True, help_text='部署服务器')
    deploy_port = models.IntegerField(blank=True, null=True, help_text='部署服务器端口')
    is_start_service = models.NullBooleanField(blank=True, null=True, default=False, help_text='是否启动服务')
    deploy_docker_run = models.CharField(max_length=1000, blank=True, null=True, help_text='部署的docker run字符串')
    success_image_callback = models.CharField(max_length=2000, blank=True, null=True, help_text='成功生成镜像后的操作')
    docker_img_name = models.CharField(max_length=500, blank=True, null=True, help_text='项目镜像名称')
    deploy_container_name = models.CharField(max_length=500, blank=True, null=True, help_text='项目容器名称')

    class Meta:
        db_table = 'project_center'


class ProjectDockerInfo(models.Model):
    status_options = (
        ('0', '等待中'),
        ('1', '进行中'),
        ('2', '成功'),
        ('3', '失败')
    )

    salt_minion = models.ForeignKey(SaltMinion, help_text='主机服务器')
    port = models.CharField(max_length=100, blank=True, null=True, help_text='项目所在服务器端口')
    project = models.ForeignKey(ProjectCenter, help_text='项目')
    docker_img = models.CharField(max_length=500, help_text='项目镜像名称')
    docker_container = models.CharField(max_length=500, help_text='项目容器名称')
    deploy_docker_run = models.CharField(max_length=1000, blank=True, null=True, help_text='启动容器的字符串')
    progress = models.IntegerField(blank=True, null=True, default=0, help_text='进度')
    status = models.CharField(max_length=100, blank=True, null=True, choices=status_options, help_text='状态')
    message = models.CharField(max_length=255, blank=True, null=True, help_text='状态信息')
    is_start_service = models.NullBooleanField(blank=True, null=True, default=False, help_text='是否启动服务')
    generated_time = models.DateTimeField(blank=True, null=True, help_text='生成时间')
    time_consume = models.CharField(max_length=255, blank=True, null=True, help_text='耗时')

    class Meta:
        db_table = 'project_docker_info'


class ProjectImageSave(models.Model):
    status_options = (
        ('0', '等待中'),
        ('1', '进行中'),
        ('2', '成功'),
        ('3', '失败')
    )
    project = models.ForeignKey(ProjectCenter, help_text='项目')
    progress = models.IntegerField(blank=True, null=True, default=0, help_text='进度')
    status = models.CharField(max_length=100, blank=True, null=True, choices=status_options, help_text='状态')
    message = models.CharField(max_length=255, blank=True, null=True, help_text='状态信息')
    save_time = models.DateTimeField(blank=True, null=True, help_text='生成时间')

    class Meta:
        db_table = 'project_image_save'


class ProjectDeployInfo(models.Model):
    step_status_options = (
        ('0', '进行中'),
        ('1', '成功'),
        ('2', '失败')
    )

    project_docker = models.ForeignKey(ProjectDockerInfo, help_text='项目Docker信息')
    minion_id = models.CharField(max_length=1000, blank=True, null=True, help_text='服务器minion_id')
    step = models.IntegerField(blank=True, null=True, help_text='步骤')
    step_status = models.CharField(max_length=10, blank=True, null=True, choices=step_status_options,
                                   help_text='步骤的部署状态')
    title = models.CharField(max_length=500, blank=True, null=True, help_text='标题')
    content = models.TextField(blank=True, null=True, help_text='内容')

    class Meta:
        db_table = 'project_deploy_info'


class AppInstall(models.Model):
    """
    应用安装列表
    """
    name = models.CharField(max_length=200, help_text='名称', unique=True, error_messages=get_error_messages('名称'))
    version = models.CharField(max_length=100, help_text='版本', error_messages=get_error_messages('版本'),
                               blank=True, null=True)
    app_image = models.ImageField(max_length=500, upload_to='app_images/',
                                  default='app_images/default.jpg', blank=True, null=True, help_text='app的图片')
    description = models.CharField(max_length=500, blank=True, null=True, help_text='说明')
    app_sls_pkg = models.ImageField(max_length=500, upload_to='app_sls_pkgs/', blank=True, null=True,
                                    help_text='app的sls包')

    class Meta:
        db_table = 'app_install'


class AppInstallStatus(models.Model):
    """
    应用安装状态表
    """
    status_options = (
        ('0', '安装中'),
        ('1', '安装成功'),
        ('2', '安装出错'),
        ('3', '等待中')
    )
    salt_minion = models.ForeignKey(SaltMinion, help_text='salt-minion')
    app_install = models.ForeignKey(AppInstall, help_text='app的名称')
    status = models.CharField(max_length=20, default='0', choices=status_options, blank=True, null=True, help_text='状态')
    error_message = models.CharField(max_length=500, blank=True, null=True, help_text='错误信息')
    used_time = models.CharField(max_length=200, blank=True, null=True, help_text='用时')

    class Meta:
        db_table = 'app_install_status'


class OperationLog(models.Model):
    salt_minion = models.ForeignKey(SaltMinion, help_text='操作主机')
    username = models.CharField(max_length=100, blank=True, null=True, help_text='操作用户')
    operate = models.CharField(max_length=500, blank=True, null=True, help_text='执行操作')
    operate_result = models.TextField(blank=True, null=True, help_text='操作结果')

    class Meta:
        db_table = 'operation_log'


class HostPs(models.Model):
    salt_minion = models.ForeignKey(SaltMinion, help_text='主机')
    pid = models.CharField(max_length=255, blank=True, null=True, help_text='进程PID号')
    user = models.CharField(max_length=255, blank=True, null=True, help_text='进程用户')
    cpu_rate = models.CharField(max_length=100, blank=True, null=True, help_text='CPU资源占用比率')
    mem_rate = models.CharField(max_length=100, blank=True, null=True, help_text='MEM资源占用比率')
    stat = models.CharField(max_length=100, blank=True, null=True, help_text='进程状态')
    run_time = models.CharField(max_length=100, blank=True, null=True, help_text='运行时间')
    command = models.CharField(max_length=3000, blank=True, null=True, help_text='进程命令')
    view_time = models.DateTimeField(default=timezone.now, blank=True, null=True, help_text='查询时间')

    class Meta:
        db_table = 'host_ps'


class JenkinsJobs(models.Model):
    jenkins_server_url = models.CharField(max_length=2000, help_text='Jenkins服务地址')
    user_id = models.CharField(max_length=500, blank=True, null=True, help_text='Jenkins用户id')
    password = models.CharField(max_length=500, blank=True, null=True, help_text='Jenkins用户密码或token')
    job_url = models.CharField(max_length=1000, blank=True, null=True, help_text='Jenkins的连接')
    color = models.CharField(max_length=100, blank=True, null=True, help_text='颜色状态')
    job_name = models.CharField(max_length=500, blank=True, null=True, help_text='job名称')
    job_description = models.CharField(max_length=2000, blank=True, null=True, help_text='job描述')
    last_completed_build = models.CharField(max_length=4000, blank=True, null=True, help_text='上次完成构建')
    last_successful_build = models.CharField(max_length=4000, blank=True, null=True, help_text='上次成功构建')
    last_unsuccessful_build = models.CharField(max_length=4000, blank=True, null=True, help_text='上次失败构建')
    buildable = models.NullBooleanField(blank=True, null=True, help_text='是否可以构建')
    last_completed_build_info = models.TextField(blank=True, null=True, help_text='最后完成构建信息')
    last_successful_build_info = models.TextField(blank=True, null=True, help_text='最后成功构建信息')
    last_unsuccessful_build_info = models.TextField(blank=True, null=True, help_text='最后失败构建信息')
    health_report_score = models.IntegerField(blank=True, null=True, help_text='健康状态分数')
    health_report_description = models.CharField(max_length=1000, blank=True, null=True, help_text='健康状态描述')
    next_build_number = models.CharField(max_length=100, blank=True, null=True, help_text='下一个构建号')

    class Meta:
        db_table = "jenkins_jobs"


class ReceiverHooks(models.Model):
    env_options = (
        ('dev', '开发环境'),
        ('fat', '测试环境'),
        ('pro', '正式环境')
    )

    download_receiver = models.CharField(max_length=500, blank=True, null=True, help_text='导入数据的接收器地址')
    env = models.CharField(max_length=255, default='dev', choices=env_options, help_text='所属环境')
    name = models.CharField(max_length=255, help_text='工程名称')
    description = models.CharField(max_length=1000, blank=True, null=True, help_text='工程描述')
    upgrade_url = models.CharField(max_length=500, help_text='触发更新地址')
    image_label = models.CharField(max_length=100, help_text='镜像标签')
    image_lib = models.CharField(max_length=500, help_text='镜像地址')
    upgrade_time = models.DateTimeField(blank=True, null=True, help_text='更新应用时间')
    # 发布镜像到镜像库
    target_docker_hub = models.CharField(max_length=300, blank=True, null=True, help_text='目标镜像库')
    load_docker_hub = models.CharField(max_length=300, blank=True, null=True, help_text='被导入的镜像')
    is_backup = models.CharField(max_length=10, blank=True, null=True, default="1", help_text='是否备份原有镜像')
    target_docker_hub_label = models.CharField(max_length=300, blank=True, null=True, help_text='备份的镜像标签')
    target_docker_hub_username = models.CharField(max_length=300, blank=True, null=True, help_text='目标镜像库用户名')
    target_docker_hub_password = models.CharField(max_length=300, blank=True, null=True, help_text='目标镜像库用户密码')
    salt_minion_id = models.CharField(max_length=300, blank=True, null=True, help_text='操作主机')
    push_docker_hub_time = models.DateTimeField(blank=True, null=True, help_text='发布镜像时间')
    push_docker_hub_content = models.TextField(blank=True, null=True, help_text='发布镜像过程')

    class Meta:
        db_table = 'receiver_hooks'
