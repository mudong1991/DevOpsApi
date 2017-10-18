#!/bin/bash
echo "stop django-operations ---------------------"
docker stop django-operations
sudo docker ps -a | awk '{ print $1,$2 }' | grep sefon/operations| awk '{print $1 }' | xargs -I {} sudo docker rm {}
docker rm -f django-operations
docker rmi -f sefon/operations
