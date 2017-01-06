#!/bin/bash


# create image for generating cpu load

ctx download-resource containers/stress.tgz /tmp/stress.tgz

cd /tmp

tar xzf /tmp/stress.tgz

cd /tmp/stress

sudo docker build -t stress:latest .

