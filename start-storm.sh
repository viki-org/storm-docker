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

docker run -p 3773:3773 -p 3772:3772 -p 6627:6627 --name nimbus --link zookeeper:zk -h nimbus -d viki_data/storm-nimbus
docker run -p 49080:8080 --name ui --link nimbus:nimbus --link zookeeper:zk -d viki_data/storm-ui
./run-storm-supervisor.sh
