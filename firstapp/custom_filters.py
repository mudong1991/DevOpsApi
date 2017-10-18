# -*- coding: UTF-8 -*-
# __author__ = 'MD'
import django_filters
from rest_framework import filters

from firstapp import models


class SaltMinionFilter(django_filters.FilterSet):
    module = django_filters.CharFilter(method='filter_module')
    business_id = django_filters.CharFilter(method='filter_business_id')
    cluster_id = django_filters.CharFilter(method='filter_cluster_id')
    module_id = django_filters.CharFilter(method='filter_module_id')
    available = django_filters.CharFilter(method='filter_available')

    def filter_module(self, qs, name, value):
        if name and value:
            no_business_host = []
            for obj in qs:
                if obj.module.all().count() == 0:
                    no_business_host.append(obj.id)

            if str(value) == '0':
                return qs.filter(id__in=no_business_host)
            elif str(value) == '1':
                return qs.exclude(id__in=no_business_host)
            else:
                return qs
        else:
            return qs

    def filter_available(self, qs, name, value):
        if name and value:
            filter_id_list = []
            if int(value) == 1:
                for obj in qs:
                    business_list = list(set([m.business.id for m in obj.module.all() if m.business
                                              and m.name != u'空闲机' and m.name != u'故障机']))
                    if business_list:
                        filter_id_list.append(obj.id)
                return qs.filter(id__in=filter_id_list)
            else:
                return qs
        else:
            return qs

    def filter_business_id(self, qs, name, value):
        if name and value:
            filter_id_list = []
            for obj in qs:
                business_list = list(set([m.business.id for m in obj.module.all() if m.business]))
                if int(value) in business_list:
                    filter_id_list.append(obj.id)
            return qs.filter(id__in=filter_id_list)
        else:
            return qs

    def filter_cluster_id(self, qs, name, value):
        if name and value:
            filter_id_list = []
            for obj in qs:
                cluster_list = list(set([m.cluster.id for m in obj.module.all() if m.cluster]))
                if int(value) in cluster_list:
                    filter_id_list.append(obj.id)
            return qs.filter(id__in=filter_id_list)
        else:
            return qs

    def filter_module_id(self, qs, name, value):
        if name and value:
            filter_id_list = []
            if str(value) == 'free':
                for obj in qs:
                    module_list = list(set([m.id for m in obj.module.all()
                                            if m.name == u'空闲机']))
                    if module_list:
                        filter_id_list.append(obj.id)
                return qs.filter(id__in=filter_id_list)
            elif str(value) == 'fault':
                for obj in qs:
                    module_list = list(set([m.id for m in obj.module.all()
                                            if m.name == u'故障机']))
                    if module_list:
                        filter_id_list.append(obj.id)
                return qs.filter(id__in=filter_id_list)
            else:
                for obj in qs:
                    module_list = list(set([m.id for m in obj.module.all()]))
                    if int(value) in module_list:
                        filter_id_list.append(obj.id)
                return qs.filter(id__in=filter_id_list)
        else:
            return qs

    class Meta:
        model = models.SaltMinion
        fields = ['module']


class ProjectDeployInfoFilter(filters.FilterSet):

    class Meta:
        model = models.ProjectDeployInfo
        fields = ['id', 'project_docker', 'minion_id']


class ProjectDockerInfoFilter(filters.FilterSet):

    class Meta:
        model = models.ProjectDockerInfo
        fields = ['id', 'project', 'status']


class JenkinsJobsFilter(filters.FilterSet):

    class Meta:
        model = models.JenkinsJobs
        fields = ['id', 'user_id']


class ReceiverHooksFilter(filters.FilterSet):

    class Meta:
        model = models.ReceiverHooks
        fields = ['id', 'env', 'name', 'description']