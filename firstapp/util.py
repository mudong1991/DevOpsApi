# -*- coding:utf-8 -*-
# Created by Administrator at 2017/3/7 0007
"""
项目常用工具函数和接口
"""
import tarfile
import logging
import os
import time
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 定义日志器
running_log = logging.getLogger("info")
debug_log = logging.getLogger("django.request")


def file_write(path, chunks, filename):
    destination_file = os.path.join(path, filename)
    try:
        d_file = open(destination_file, 'wb+')
    except:
        raise Exception(message="目标路径无法打开")
    else:
        for c in chunks:
            d_file.write(c)
        d_file.close()


def get_page(data_list, page=1):
    """
    翻页方法
    :param data_list:
    :param page:
    :return:
    """
    per_page = settings.PAGE_SIZE
    paginator = Paginator(data_list, per_page)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items


def get_page_result(data_list, page=1):
    result = {}
    page_size = settings.PAGE_SIZE
    paginator = Paginator(data_list, page_size)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
        page = 1
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    result['tableList'] = items.object_list
    result['pageSize'] = page_size
    result['totalCount'] = paginator.count
    result['totalPage'] = paginator.num_pages
    result['pageNo'] = int(page)
    result['next'] = items.has_next() if items.has_next() else False
    result['previous'] = items.has_previous() if items.has_previous() else False
    return result


def get_appname():
    """
    获取app的名字，即包的名字
    :return: str
    """
    return __package__


def get_template(name):
    """
    :param name: 网页模板名
    :return: 网页模板(绝对路径)
    """
    if str.split(name, '.')[-1] == 'html':
        return get_appname() + "/" + name
    else:
        return get_appname() + "/" + name + ".html"


def custom_render(request, template_name, dict):
    """
    自定义render函数，为render的dict添加一些常用属性和RequestContext
    :param request: 请求
    :param template_name: 模板名字
    :param dict: 渲染的上下文字典
    :return:
    """
    dict["app_name"] = get_appname()
    return render(request, get_template(template_name), dict)


def time_calculator(atime, btime):
    """
    :param atime: 第一个时间
    :param btime: 第二个时间
    :return: 相差的秒数(a-b)
    """
    time_a = time.mktime(time.strptime(atime, settings.TIME_FORMAT))
    time_b = time.mktime(time.strptime(btime, settings.TIME_FORMAT))
    seconds = time_a - time_b
    return seconds


def time_calculator_seconds(atime, seconds):
    """
    :param atime: 第一个时间
    :param seconds: 小于这个时间的秒数
    :return: 相减格式化后的时间
    """
    time_a = time.mktime(time.strptime(atime, settings.TIME_FORMAT))
    time_b = time_a - seconds
    btime = time.strftime(settings.TIME_FORMAT, time.localtime(time_b))
    return btime


def get_current_time():
    """
    :return: 当前的时间字符串
    """
    time_string = time.strftime(settings.TIME_FORMAT, time.localtime(time.time()))
    return time_string


def make_tar(file_name, source_dir):
    """
    将目录打包成tar
    :param file_name: 文件名字，可以是路径，文件名必须是tar后缀
    :param source_dir: 打包的目录路径
    :return:
    """
    with tarfile.open(file_name, "w") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def make_targz(file_name, source_dir):
    """
    将目录打包压缩成tar.gz
    :param file_name: 文件名字，可以是路径，文件名必须是tar.gz后缀
    :param source_dir: 打包的目录路径
    :return:
    """
    with tarfile.open(file_name, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))