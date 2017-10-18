FROM daocloud.io/python:2.7
MAINTAINER mudong  <blog.scmud.com>
ENV PYPYTHONUNBUFFERED 1
ADD operations.tar /var/www/operations
WORKDIR /var/www/operations
RUN pip install --no-index --find-links=./docker/whl_home/ -r requirements.txt