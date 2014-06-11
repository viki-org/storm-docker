#!/bin/bash

# Used to stop running storm-docker Docker containers.
#
# To stop every storm-docker Docker container, don't supply any args:
#
#     ./destroy-storm.sh
#
# To stop the `nimbus` and `ui` containers:
#
#    ./destroy-storm.sh nimbus ui

function stop_storm_docker {
  docker stop $1; docker rm $1
}

if [ $# -eq 0 ]
then
  stop_storm_docker ui
  stop_storm_docker supervisor
  stop_storm_docker nimbus
  stop_storm_docker zookeeper
else
  for component in "$@"
  do
    stop_storm_docker $component
  done
fi
