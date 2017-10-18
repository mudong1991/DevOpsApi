#!/bin/bash
echo '---------------migrate database main------------------------'
docker exec -it django-operations python manage.py migrate
