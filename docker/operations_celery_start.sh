#!/bin/bash
echo '--------------- Start celery ------------------------'
docker exec -idt django-operations python manage.py celery -A Operations worker -l info
yum install gcc libffi-devel python-devel openssl-devel -y
pip install  -r ../requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
python manage.py celery -A Operations worker -l info