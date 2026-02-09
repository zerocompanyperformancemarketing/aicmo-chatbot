#!/bin/bash

sudo docker compose down
# STOP ALL DOCKER RUNNING IN DEV
sudo docker stop $(sudo docker ps -q) && sudo docker rm $(sudo docker ps -a -q)

# remove dangling images
sudo docker rmi -f $(sudo docker images --filter "dangling=true" -q --no-trunc)
sudo docker network prune -f
sudo docker volume prune -f
sudo docker builder prune -f