# -*- coding:utf-8 -*-
# file: jenkins-test
# author: Mundy
# date: 2017/8/23 0023
"""
Jenkins测试模块
"""
import jenkins


# 定义远程的jenkins master server的url，以及port
jenkins_server_url = "http://193.168.0.200:28080/"

# 定义用户的User Id 和 API Token，获取方式同上文
user_id = "mudong"
password = "123456"

# 实例化jenkins对象，连接远程的jenkins master server
server = jenkins.Jenkins(jenkins_server_url, username=user_id, password=password)
print server.get_build_console_output("AutoTest".encode('utf-8'), 10)
# print server.get_nodes()
# all_jobs = server.get_all_jobs()
# for c in all_jobs:
#     print "------------------------------------------------------------------------------------------------------------"
#     # for a,b in dict(c).items():
#     #     print str(a) + ":" + str(b)
#
#     d = server.get_job_info(name=c['name'])
#     for index, value in dict(d).items():
#         print str(index) + ":" + str(value)
# print server.get_job_info(name='governance')
# build_info = server.get_build_info('datacenter', 1)
# print build_info
# build_info =  server.get_build_info('auth', 27)
# # print '-------------------'
# for a,b in build_info.items():
#     print str(a) + ":" + str(b)


# print server.build_job('sms')
# build_info = server.get_build_info('sms', server.get_job_info('sms')['lastBuild']['number'])
# for index, value in dict(build_info).items():
#     print str(index) + ":" + str(value)
# print build_info['result']
