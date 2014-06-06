#!/bin/bash

ZOOKEEPER=`docker ps -a | awk '{print $NF}'  | grep "zookeeper$"`
ZOOKEEPER_RUNNING=$?
if [ $ZOOKEEPER_RUNNING -eq 0 ] ;
then
  echo "Zookeeper is already running"
else
  echo "Starting Zookeeper"
  scripts/run-zookeeper.sh \
    -p 2181:2181 -p 2888:2888 -p 2888:2888/udp -p 3888:3888 \
    -p 127.0.0.1:49122:22 \
    -h zookeeper --name zookeeper \
    -d viki_data/zookeeper
fi

scripts/run-storm-docker-component.sh \
  -p 3773:3773 -p 3772:3772 -p 6627:6627 \
  --name nimbus \
  --link zookeeper:zk \
  -h nimbus \
  -d viki_data/storm-nimbus

scripts/run-storm-docker-component.sh \
  -p 49080:8080 \
  --name ui \
  --link nimbus:nimbus --link zookeeper:zk \
  -d viki_data/storm-ui

scripts/run-storm-supervisor.sh \
  --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.8.4 \
  -p 49000:8000 -p 127.0.0.1:49022:22 \
  -p 6700:6700 -p 6701:6701 -p 6702:6702 -p 6703:6703 \
  --name supervisor \
  -d viki_data/storm-supervisor
