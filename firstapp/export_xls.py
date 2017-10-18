# -*- coding: UTF-8 -*-
__author__ = 'MD'
import xlwt
import xlrd
import os
from django.conf import settings
from django.db import (transaction, connection)
from firstapp import models


# 导出到execl
class ExcelExporter(object):
    def __init__(self,  file_name, data_list, headers, data_item, title):
        self.file_name = file_name
        self.data_list = data_list
        self.headers = headers
        self.data_item = data_item
        self.title = title

    def __call__(self, *args, **kwargs):
        if len(self.data_list) > 0:
            # 建立工作表
            wb = xlwt.Workbook(encoding='utf-8')
            sheet = wb.add_sheet(self.file_name)
            # 新建样式
            easyxf_title = xlwt.easyxf('pattern:pattern solid,fore_colour lime;'
                                       'align:vertical center, horizontal center;'
                                       'font: bold true, colour black, height 400;'
                                       'border: top thin,bottom thin, left thin,right thin;')
            easyxf_header = xlwt.easyxf('pattern:pattern solid,fore_colour rose;'
                                        'align:vertical center, horizontal center;'
                                        'font: bold true, colour black;'
                                        'border: top thin,bottom thin, left thin,right thin;')
            easyxf_1 = xlwt.easyxf('pattern:pattern solid,fore_colour light_green;'
                                   'align:vertical center, horizontal center, wrap on;'
                                   'font: colour black;'
                                   'border: top thin,bottom thin, left thin,right thin;')
            easyxf_2 = xlwt.easyxf('pattern:pattern solid,fore_colour pale_blue;'
                                   'align:vertical center, horizontal center, wrap on;'
                                   'font: colour black;'
                                   'border: top thin,bottom thin, left thin,right thin;')  # wrap on 为自动换行
            # 写入大标题
            sheet.write_merge(0, 0, 0, len(self.headers) - 1, self.title, easyxf_title)

            # 写入第一行头信息
            for index, item in enumerate(self.headers):
                sheet.col(index).width = 6666
                sheet.row(1).set_style(xlwt.easyxf('font:height %s' % 300))
                sheet.write(1, index, item, easyxf_header)

            # 写入数据信息
            for index, data in enumerate(self.data_list):
                for i, key in enumerate(self.data_item):
                    sheet.row(index+2).set_style(xlwt.easyxf('font:height %s' % 300))
                    if (index+2) % 2 == 0:
                        sheet.write(index+2, i, data[key], easyxf_1)
                    else:
                        sheet.write(index+2, i, data[key], easyxf_2)

            # 将文件保存到临时文件目录中
            file_name = self.file_name+'.xls'
            fileapath = os.path.join(settings.MEDIA_ROOT, "tempfiles", file_name)
            if os.path.exists(fileapath):
                os.remove(fileapath)
                wb.save(fileapath)
            else:
                wb.save(fileapath)

            return file_name
        else:
            return None