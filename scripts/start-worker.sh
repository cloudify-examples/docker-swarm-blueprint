#!/bin/bash

ctx logger info "MASTER IP=$MASTERIP"

sudo docker swarm join --advertise-addr $IP --token $TOKEN $MASTERIP

