#!/bin/bash

sudo sh -c 'echo DOCKER_OPTS=\"-H tcp://0.0.0.0:2375\" >> /etc/default/docker'

sudo service docker restart

sleep 2

sudo docker -H localhost:2375 swarm init --advertise-addr $IP


ctx instance runtime-properties manager_token $(sudo docker -H localhost:2375 swarm join-token -q manager)
ctx instance runtime-properties worker_token $(sudo docker -H localhost:2375 swarm join-token -q worker)

# Install compose

sudo curl -L "https://github.com/docker/compose/releases/download/1.9.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# If there are existing nodes, tell them to rejoin (heal scenario)

# TBD
