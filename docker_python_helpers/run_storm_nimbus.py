# This script is used to start either or both of:
# (a) Zookeeper ambassador container on a machine running the Nimbus docker
#     container (but which does not run a Zookeeper docker container)
# (b) Nimbus docker container

# Usage:
#
#     python -m docker_python_helpers/run_storm_nimbus.py <ARGS>

from __future__ import print_function

from . import docker_run

import argparse
import os
import sys

# When run as a main program
if __name__ == "__main__":
  # This script is used like
  #     `python -m docker_python_helpers/run_storm_nimbus.py <ARGS>`
  # hence the need for subscripting `sys.argv` from 2
  actual_args = sys.argv[2:]
  zk_ambassador_args = None
  storm_nimbus_args = None
  try:
    nimbus_args_after_this_idx = actual_args.index("--nimbus-args-after-this")
    zk_ambassador_args = actual_args[:nimbus_args_after_this_idx]
    storm_nimbus_args = actual_args[nimbus_args_after_this_idx + 1:]
  except ValueError:
    zk_ambassador_args = actual_args

  storm_config = docker_run.get_storm_config()

  if zk_ambassador_args is not None:
    # Gotta run the Zookeeper ambassador docker container.
    # Based on convention, we pick the 0th Zookeeper server because that server
    # will have a running Zookeeper ambassador docker container as well.
    servers = storm_config["servers"]
    storm_yaml_config = storm_config["storm.yaml"]
    zk_server = servers[storm_yaml_config["storm.zookeeper.servers"][0]]
    zk_port = storm_yaml_config["storm.zookeeper.port"]
    zk_follower_port = storm_config["zookeeper.multiple.setup"]["follower.port"]
    zk_election_port = storm_config["zookeeper.multiple.setup"]["election.port"]
    # Setup the Zookeeper ambassador docker container's exposed ports and
    # environment variables
    zk_port_and_env_args = [
      "--expose {}".format(zk_port),
      "--expose {}".format(zk_follower_port),
      "--expose {}".format(zk_election_port),
      "-e ZK_PORT_{}_TCP=tcp://{}:{}".format(zk_port, zk_server, zk_port),
      "-e ZK_PORT_{}_TCP=tcp://{}:{}".format(
        zk_follower_port, zk_server, zk_follower_port
      ),
      "-e ZK_PORT_{}_UDP=udp://{}:{}".format(
        zk_follower_port, zk_server, zk_follower_port
      ),
      "-e ZK_PORT_{}_TCP=tcp://{}:{}".format(
        zk_election_port, zk_server, zk_election_port
      ),
    ]
    zk_ambassador_docker_run_cmd = \
      "docker run {port_and_env_args} {zk_ambassador_args}".format(
        port_and_env_args=" ".join(zk_port_and_env_args),
        zk_ambassador_args=" ".join(zk_ambassador_args)
      )
    print(zk_ambassador_docker_run_cmd)
    os.system(zk_ambassador_docker_run_cmd)

  if storm_nimbus_args is not None:
    docker_run.main(storm_nimbus_args)
