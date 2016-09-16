#!/bin/bash

sudo docker swarm init --advertise-addr $IP

ctx instance runtime-properties manager_token $(sudo docker swarm join-token -q manager)
ctx instance runtime-properties worker_token $(sudo docker swarm join-token -q worker)

# If there are existing nodes, tell them to rejoin (heal scenario)


