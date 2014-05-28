#!/bin/bash

ZOOKEEPER=`docker ps -a | awk '{print $NF}'  | grep "zookeeper$"`
ZOOKEEPER_RUNNING=$?
if [ $ZOOKEEPER_RUNNING -eq 0 ] ;
then
    echo "Zookeeper is already running"
else
    echo "Starting Zookeeper"
    docker run -p 2181:2181  -h zookeeper --name zookeeper -d viki_data/zookeeper
fi

./run-storm-docker-component.sh -p 3773:3773 -p 3772:3772 -p 6627:6627 --name nimbus --link zookeeper:zk -h nimbus -d viki_data/storm-nimbus
./run-storm-docker-component.sh -p 49080:8080 --name ui --link nimbus:nimbus --link zookeeper:zk -d viki_data/storm-ui
./run-storm-supervisor.sh \
  --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.8.4 \
  -p 49000:8000 -p 127.0.0.1:49022:22 \
  -p 6700:6700 -p 6701:6701 -p 6702:6702 -p 6703:6703 \
  --name supervisor \
  -d viki_data/storm-supervisor
