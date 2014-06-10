#!/bin/bash

ZOOKEEPER=`docker ps -a | awk '{print $NF}'  | grep "zookeeper$"`
ZOOKEEPER_RUNNING=$?
if [ $ZOOKEEPER_RUNNING -eq 0 ] ;
then
  echo "Zookeeper is already running"
else
  echo "Starting Zookeeper"
  SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-zookeeper.sh \
    -p 127.0.0.1:49122:22 \
    -h zookeeper --name zookeeper \
    -d viki_data/zookeeper
fi

SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-docker-component.sh \
  --name nimbus \
  --link zookeeper:zk \
  -h nimbus \
  -d viki_data/storm-nimbus \
  --storm-docker-component nimbus \
  --storm-docker-component drpc

SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-docker-component.sh \
  --name ui \
  --link nimbus:nimbus --link zookeeper:zk \
  -d viki_data/storm-ui \
  --storm-docker-component ui

SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-supervisor.sh \
  --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.8.4 \
  -p 127.0.0.1:49022:22 \
  --name supervisor \
  -d viki_data/storm-supervisor
