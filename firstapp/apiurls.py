# -*- coding:utf-8 -*-
# file: apiurls
# author: Mundy
# date: 2017/5/26 0026
"""
api的相关路由
"""
from rest_framework import routers
from django.conf.urls import url
from firstapp import apiviews
from firstapp.dev_cloud_views import auth_views

urlpatterns = [
    url(r'^login/', auth_views.LoginView.as_view(), name='login'),
    url(r'^check_login/', auth_views.CheckLoginView.as_view(), name='check_login')
]

route = routers.DefaultRouter()
# 代理设置
route.register(r'salt_master', apiviews.SaltMasterViewSet)
route.register(r'salt_minion', apiviews.SaltMinionViewSet)
# 主机资源管理
route.register(r'business_admin', apiviews.BusinessAdminViewSet)
route.register(r'module', apiviews.ModuleViewSet)
route.register(r'cluster', apiviews.ClusterViewSet)
# 自动部署
route.register(r'project_center', apiviews.ProjectCenterViewSet)
route.register(r'project_docker_info', apiviews.ProjectDockerInfoViewSet)
route.register(r'project_deploy_info', apiviews.ProjectDeployInfoViewSet)
route.register(r'app_install', apiviews.AppInstallViewSet)
route.register(r'app_install_status', apiviews.AppInstallStatusViewSet)
# 持续集成
route.register(r'jenkins_jobs', apiviews.JenkinsJobsViewSet)
route.register(r'receiver_hooks', apiviews.ReceiverHooksViewSet)

urlpatterns += route.urls
