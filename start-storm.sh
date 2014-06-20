#!/bin/bash

# This is used to run a Docker container in this repository after you have
# run the `make` command to build the Docker images.

# Inspects the `IMAGE` column of the output of `docker ps` to see if the given
# Docker container is running
function is_docker_container_running {
  docker ps | tail -n+2 | awk '{print $2}' | grep --quiet $1
}

# Skip `pip install` step for scripts in the `scripts` folder if the
# `SKIP_PIP_INSTALL` file is present.
SKIP_PIP_INSTALL="false"
if [[ -f SKIP_PIP_INSTALL ]]
then
  SKIP_PIP_INSTALL="true"
fi

# Starts a given storm-docker Docker container
function start_storm_docker {
  case $1 in
  nimbus)
    if is_docker_container_running "viki_data/storm-nimbus"
    then
      echo "storm nimbus Docker container already running"
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-docker-component.sh \
        --name nimbus \
        --link zookeeper:zk \
        -h nimbus \
        -d viki_data/storm-nimbus \
        --storm-docker-component nimbus \
        --storm-docker-component drpc
    fi
    ;;
  supervisor)
    if is_docker_container_running "viki_data/storm-supervisor"
    then
      echo "storm supervisor Docker container already running"
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-supervisor.sh \
        --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.4.4 \
        -p 127.0.0.1:49022:22 \
        --name supervisor \
        -d viki_data/storm-supervisor
    fi
    ;;
  ui)
    if is_docker_container_running "viki_data/storm-ui"
    then
      echo "storm ui Docker container already running"
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-docker-component.sh \
        --name ui \
        --link nimbus:nimbus --link zookeeper:zk \
        -d viki_data/storm-ui \
        --storm-docker-component ui
    fi
    ;;
  zookeeper)
    if is_docker_container_running "viki_data/zookeeper"
    then
      echo "zookeeper Docker container already running"
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-zookeeper.sh \
        -p 127.0.0.1:49122:22 \
        -h zookeeper --name zookeeper \
        -d viki_data/zookeeper
    fi
    ;;
  *)
    echo "Unknown storm-docker component: \"$1\""
    ;;
  esac
}

# Execution of this bash script starts from here
if [ $# -eq 0 ]
then
  # No arguments supplied to this script; run every component
  start_storm_docker "zookeeper"
  start_storm_docker "nimbus"
  start_storm_docker "ui"
  start_storm_docker "supervisor"
elif [ "$1" = "--help" ]
then
  echo "Runs a Docker container built by this repository."
  echo "You can supply one or more of the following args:"
  echo ""
  echo "    nimbus     - Runs the nimbus container (components:" \
    "Storm Nimbus, Storm DRPC)"
  echo "    supervisor - Runs the supervisor container (components:" \
    "Storm Supervisor, Storm Logviewer)"
  echo "    ui         - Runs the ui container (components: Storm UI)"
  echo "    zookeeper  - Runs the zookeeper container (components: Zookeeper)"
  echo ""
  echo "For example, to run the zookeeper and ui containers, run:"
  echo ""
  echo "    ./start-storm.sh zookeeper ui"
  echo ""
else
  # At least one argument was supplied to this script.
  # We start each Docker container in the arguments.
  for component in "$@"
  do
    start_storm_docker $component
  done
fi
