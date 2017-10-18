# -*-coding:utf-8-*-
# __author__ = 'MD'
import os, re
import shutil
from custom_gittle import Gittle, GittleAuth
from dulwich.errors import NotGitRepository, GitProtocolError


repo_path = os.path.join(os.path.abspath('/tmp/'), u'四方品台')
repo_url = u'https://git.oschina.net/cdsfkj/devops.git'.encode('utf-8')
auth_info = GittleAuth(username=u'mudong@sefon.com', password=u'dong523554')

if os.path.exists(repo_path):
    shutil.rmtree(repo_path)

# 克隆仓库

repo_obj = Gittle.clone(repo_url, repo_path, auth=auth_info, branch_name=None)

#
# # pull
# # repo = Gittle.clone(repo_path, origin_uri=repo_url, auth=auth_info)
# # print repo.branches