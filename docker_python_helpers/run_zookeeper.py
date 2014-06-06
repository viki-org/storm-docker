# This script is used to run a Docker container with `storm-supervisor`.
# Usage:
#
#     python -m docker_python_helpers/run_zookeeper.py <ARGS>

import os
import os.path
import re
import sys

from . import docker_run

if __name__ == "__main__":
  ipv4Addresses = docker_run.get_ipv4_addresses()
  stormConfig = docker_run.get_storm_config()
  foundCurrentServer = False
  for zkIpAddress in stormConfig["storm.yaml"]["storm.zookeeper.servers"]:
    if zkIpAddress in ipv4Addresses:
      foundCurrentServer = True
      break
  if not foundCurrentServer:
    raise RuntimeError(re.sub("\s+", " ",
      """IP address of this machine does not match any IP address supplied in
      the `storm.yaml` -> `storm.zookeeper.servers` section of
      `config/storm-supervisor.yaml`.
      """).strip()
    )

  dockerRunArgs = docker_run.construct_docker_run_args(
    myIPv4Addresses=ipv4Addresses,
    # See the usage of this script at the top of the file... and you'll
    # understand why we need to subscript `sys.argv` from 2
    dockerRunArgv=sys.argv[2:],
  )
  dockerRunCmd = "docker run {}".format(dockerRunArgs)
  print(dockerRunCmd)
  os.system(dockerRunCmd)
