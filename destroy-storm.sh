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
  stop_storm_docker zk_ambassador
  stop_storm_docker zookeeper
else
  for component in "$@"
  do
    case $component in
      zookeeper-with-ambassador)
        stop_storm_docker zk_ambassador
        stop_storm_docker zookeeper
        ;;
      nimbus-with-zookeeper-ambassador)
        stop_storm_docker nimbus
        stop_storm_docker zk_ambassador
        ;;
      ui-on-zk-ambassador-machine)
        stop_storm_docker ui
        ;;
      *)
        stop_storm_docker $component
        ;;
    esac
  done
fi
