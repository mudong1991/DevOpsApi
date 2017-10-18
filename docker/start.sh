#!/bin/bash
echo "Install pip......"
if [ ! -f "./get-pip.py" ]; then
wget https://bootstrap.pypa.io/get-pip.py
fi
python get-pip.py
echo "Download python wheel package......"
mkdir ./whl_home
pip install --download ./whl_home -r ../requirements.txt  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "Packaging operations project ......"
tar -cf operations.tar -C ../ ./
echo "Build sefon/operations docker image start ......"
docker build -t sefon/operations ./
echo "Start django-operations ......"
docker run --name django-operations -v /var/www/operations -p 8810:8000 -d sefon/operations /usr/local/bin/uwsgi --http :8000 --chdir /var/www/operations --static-map /static=/var/www/operations/static --static-map /media=/var/www/operations/media -w Operations.wsgi
