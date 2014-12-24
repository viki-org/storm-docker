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
  nimbus-with-zookeeper-ambassador)
    # Implemented for https://github.com/viki-org/storm-docker/issues/5
    # which lets the user run the Nimbus docker container on a separate physical
    # machine from any of the machine(s) running a Zookeeper docker container.

    # This server will run a Zookeeper along with an ambassador.
    # We add a `--dont-expose-ports` argument to get the
    # `docker_python_helpers/run-zookeeper.py` script to generate a `docker run`
    # command without `-p` flags that expose the ports on the host machine.
    if is_docker_container_running "viki_data/storm-nimbus" && \
        is_docker_container_running "zk_ambassador"
    then
      echo "storm nimbus Docker container already running"
      echo "zookeeper ambassador Docker container already running"
    elif is_docker_container_running "viki_data/storm-nimbus"
    then
      echo "storm nimbus Docker container already running"
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-nimbus.sh \
        --name zk_ambassador -h zk_ambassador -d svendowideit/ambassador
    elif is_docker_container_running "zk_ambassador"
    then
      echo "zookeeper ambassador Docker container already running"
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-nimbus.sh \
        --nimbus-args-after-this \
        --name nimbus \
        --link zk_ambassador:zk \
        -h nimbus \
        -d viki_data/storm-nimbus \
        --storm-docker-component nimbus \
        --storm-docker-component drpc
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-nimbus.sh \
        --name zk_ambassador -h zk_ambassador -d svendowideit/ambassador \
        --nimbus-args-after-this \
        --name nimbus \
        --link zk_ambassador:zk \
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
  ui-on-zk-ambassador-machine)
    if is_docker_container_running "viki_data/storm-ui"
    then
      echo "storm ui Docker container already running"
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-storm-docker-component.sh \
        --name ui \
        --link nimbus:nimbus --link zk_ambassador:zk \
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
  zookeeper-with-ambassador)
    # This server will run a Zookeeper along with an ambassador.
    # We add a `--dont-expose-ports` argument to get the
    # `docker_python_helpers/run-zookeeper.py` script to generate a `docker run`
    # command without `-p` flags that expose the ports on the host machine.
    if is_docker_container_running "viki_data/zookeeper" && \
        is_docker_container_running "zk_ambassador"
    then
      echo "zookeeper Docker container already running"
      echo "zookeeper ambassador Docker container already running"
    elif is_docker_container_running "viki_data/zookeeper"
    then
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-zookeeper.sh \
        --no-zookeeper \
        -- \
        --link zookeeper:zk --name zk_ambassador -d svendowideit/ambassador
    elif is_docker_container_running "zk_ambassador"
    then
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-zookeeper.sh \
        -p 127.0.0.1:49122:22 \
        -h zookeeper --name zookeeper \
        -d viki_data/zookeeper \
        --no-dash-p
    else
      SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL scripts/run-zookeeper.sh \
        -p 127.0.0.1:49122:22 \
        -h zookeeper --name zookeeper \
        -d viki_data/zookeeper \
        --no-dash-p \
        -- \
        --link zookeeper:zk --name zk_ambassador -d svendowideit/ambassador
    fi
    ;;
  *)
    echo "Unknown storm-docker component: \"$1\""
    ;;
  esac
}

# Execution of this bash script starts from here
if [ $# -eq 0 ] || [ "$1" = "--help" ]
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
  echo "    all        - Runs all the above"
  echo ""
  echo "For example, to run the zookeeper and ui containers, run:"
  echo ""
  echo "    ./start-storm.sh zookeeper ui"
  echo ""
elif [ "$1" = "all" ]
then
  # No arguments supplied to this script; run every component
  start_storm_docker "zookeeper"
  start_storm_docker "nimbus"
  start_storm_docker "ui"
  start_storm_docker "supervisor"
else
  # At least one argument was supplied to this script.
  # We start each Docker container in the arguments.
  for component in "$@"
  do
    start_storm_docker $component
  done
fi
