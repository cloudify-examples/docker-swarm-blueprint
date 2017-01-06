#!/bin/bash

ctx logger info "MASTER IP=$MASTERIP"

#if [ ! -z "$LABEL" ]; then
#  # UBUNTU SPECIFIC
#  sudo grep -q '^DOCKER_OPTS'
#  if [ $? -eq 0 ]; then
#    ctx logger info "RUNNING SED"
#    sudo sed -i /etc/default/docker -e "s/^DOCKER_OPTS=\"\(.*\)\"/DOCKER_OPTS=\"\1 --label=$LABEL\"/"
#  else
#    ctx logger info "RUNNING ECHO"
#    sudo sh -c "echo \"DOCKER_OPTS=\\\"--label=$LABEL\\\"\" >> /etc/default/docker"
#  fi
#
#  ctx logger info "RESTART DOCKER"
#  sudo service docker restart
#fi

sudo docker swarm join --advertise-addr $IP --token $TOKEN $MASTERIP

HOSTNAME=`hostname`
ctx logger info "GETTING ID: MASTER=${MASTERIP} HN=${HOSTNAME}"
NODE_ID=`sudo docker -H "${MASTERIP}:2375" node ls -q -f name=${HOSTNAME}`
ctx logger info "GOT NODE ID: ${NODE_ID}"
sudo docker -H "${MASTERIP}:2375" node update --label-add "role=worker" "${NODE_ID}"
