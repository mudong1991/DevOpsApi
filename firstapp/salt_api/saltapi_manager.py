# -*- coding:utf-8 -*-
# file: saltapi_manager
# author: Mundy
# date: 2017/5/10 0010
"""
salt api 管理
"""
import requests
import json
from requests.exceptions import ConnectionError, ConnectTimeout


def salt_response_return(response):
    return response.json()['return']


# --------requests设置--------
time_out = 16
headers = {
    'content-type': 'application/json',
    'Accept': 'application/json',
}
request_session = requests.Session()
request_session.headers.update(headers)
request_session.verify = False


# ----------认证---------
def login_salt(request_url, username, password, eauth):
    request_url = request_url if str(request_url).endswith("/") else (request_url + "/")
    try:
        response_login = request_session.post(request_url + 'login/',
                             data=json.dumps({'username': username, 'password': password, 'eauth': eauth}),
                             timeout=time_out)
    except ConnectionError:
        return False, 'salt-master服务端连接失败！'
    except Exception as e:
        return False, 'salt-master服务端连接失败！'
    else:
        if response_login.status_code != 200:
            return False, 'salt-master服务端认证失败或认证信息过期，请重新认证！'
        return True, salt_response_return(response_login)[0]['token']


# ----------获取所有主机----------------
def get_all_host(request_url, token):
    request_url = request_url if str(request_url).endswith("/") else (request_url + "/")
    request_session.headers.update({'X-Auth-Token': token})
    # 获取主机列表
    try:
        response_minions = request_session.get(request_url + 'minions/', timeout=time_out)
    except Exception as e:
        return False, 'salt-master服务端连接失败！'
    else:
        if response_minions.status_code != 200:
            return False, 'salt-master服务端认证失败或认证信息过期，请重新认证！'
        return True, salt_response_return(response_minions)


# ----------执行命令--------------
def minion_run(request_url, username, password, eauth, tgt_id, fun, cmd_str=None):
    request_url = request_url if str(request_url).endswith("/") else (request_url + "/")
    # 执行命令
    try:
        if cmd_str:
            response_minions = request_session.post(request_url + 'run/', data=json.dumps([{'client': 'local', 'tgt': tgt_id, 'fun': fun,
                                                           'arg': cmd_str, 'username': username, 'password': password, 'eauth': eauth}]))
        else:
            response_minions = request_session.post(request_url + 'run/',
                                                    data=json.dumps([{'client': 'local', 'tgt': tgt_id, 'fun': fun,
                                                                      'username': username,
                                                                      'password': password, 'eauth': eauth}]),
                                                    )
    except Exception as e:
        print e
        return False, 'salt-master服务端连接失败！'
    else:
        if response_minions.status_code != 200:
            return False, 'salt-master服务端认证失败或认证信息过期，请重新认证！'

        if not salt_response_return(response_minions)[0].has_key(tgt_id):
            return False, '目标主机没有响应！'

        return True, salt_response_return(response_minions)


if __name__ == '__main__':
    request_url = 'https://120.76.228.102:4507/'
    username = 'sefon'
    password = '1234abcd'
    eauth = 'pam'
    # print login_salt(request_url, username, password, eauth)
    # # print get_all_host(request_url, '25844db97aa7bdafa0288afec305c8a3b088e132')
    # print minion_run(request_url, username, password, eauth, '131.10.10.104', 'cmd.run',
    #                  "python /srv/salt/auto_deploy_java.py 'https://git.oschina.net/sefang/run.git' 'mudong@sefon.com'"
    #                  " 'dong523554' 'develop' 'run'")
    # print minion_run(request_url, username, password, eauth, '131.10.10.103', 'state.sls',
    #                  "git")
    test_str = minion_run(request_url, username, password, eauth, '193.168.0.91', 'cmd.run',
                     "ps -aeo pid,user,%cpu,%mem,stat,time,command --sort -%mem")[1][0][u'193.168.0.91']
    a1= test_str.split('\n')
    tmp = []
    import re
    for index, i in enumerate(a1):
        if index > 1:
            all_info = re.findall('(\S+)', i)
            result = {'pid': all_info[0], 'user': all_info[1], 'cpu': all_info[2], 'mem': all_info[3], 'stat': all_info[4],
                     'time': all_info[5], 'command': ' '.join(all_info[6:])}
            if float(result['cpu']) >0 or float(result['mem']) >0:
                tmp.append(result)

    for i in tmp:
        print i

