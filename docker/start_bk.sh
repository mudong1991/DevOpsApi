#!/bin/bash
echo "Packaging operations project ......"
tar -cf operations.tar -C ../ ./
echo "Build sefon/operations docker image start ......"
docker build -t sefon/operations ./
echo "Start django-operations ......"
docker run --name django-operations -v /var/www/operations:/var/www/operations -p 8810:8000 -d sefon/operations python manage.py runserver 0.0.0.0:8000