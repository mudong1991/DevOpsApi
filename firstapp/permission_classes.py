# -*- coding: UTF-8 -*-
__author__ = 'MD'

from rest_framework import permissions
from django.contrib.auth.models import Group


# 模型的权限
class ModelPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.read_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


# 基础认证用户权限
class BaseAuthUserPermission(permissions.BasePermission):
    def __init__(self):
        self.admin_group = Group.objects.get(name="安全管理员")
        self.manager_group = Group.objects.get(name="系统管理员")
        self.log_group = Group.objects.get(name="审计管理员")


# 认证用户权限
class AuthUserPermission(BaseAuthUserPermission):
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = request.user
        user_groups = user.groups.all()
        if request.method == "GET":
            if self.manager_group in user_groups:
                return True
            else:
                return False
        else:
            return True


# 安全管理员权限
class AdminPermission(BaseAuthUserPermission):
    def has_permission(self, request, view):
        if self.admin_group in request.user.groups.all():
            return True
        else:
            return False


# 系统管理员权限
class ManagerPermission(BaseAuthUserPermission):
    def has_permission(self, request, view):
        if self.manager_group in request.user.groups.all():
            return True
        else:
            return False


# 审计管理员权限
class LogPermission(BaseAuthUserPermission):
    def has_permission(self, request, view):
        if self.log_group in request.user.groups.all():
            return True
        else:
            return False


# 审计和安全管理员权限
class LogAndAdminPermission(BaseAuthUserPermission):
    def has_permission(self, request, view):
        if self.log_group or self.admin_group in request.user.groups.all():
            return True
        else:
            return False
