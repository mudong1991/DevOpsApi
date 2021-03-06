# -*- coding:utf-8 -*-
# file: user_admin
# author: Mundy
# date: 2017/11/8 0008
"""
系统设置相关API视图
"""
from rest_framework import viewsets
from firstapp import models
from rest_framework import filters
from firstapp.pagination import CustomPagination
from rest_framework.decorators import list_route, detail_route
from firstapp.apiviews_utils import catch_exception_response, GridOrderingFilter
from firstapp.system_settings_views import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from firstapp.permission_classes import ModelPermission


class UserAdminSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, GridOrderingFilter)
    filter_fields = ('username', )
    search_fields = ('$username', )
    pagination_class = CustomPagination
    permission_classes = [ModelPermission]

    @list_route(methods=['DELETE'])
    def delete_user(self, request):
        user_id_list = request.data
        for user_id in user_id_list:
            try:
                models.User.objects.get(pk=user_id).delete()
            except:
                pass
        return Response('ok')