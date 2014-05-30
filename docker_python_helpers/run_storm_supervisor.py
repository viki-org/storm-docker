# This script is used to run a Docker container with `storm-supervisor`.
# Usage:
#
#     python -m docker_python_helpers/run_storm_supervisor.py <ARGS>

import os
import os.path
import re
import sys
import yaml

from . import docker_run

def get_storm_config():
  """Returns the Dict defined by the `config/storm-setup.yaml` file.

  Returns:
    Dict: the Dict defined by the `config/storm-setup.yaml` file."""
  with open(os.path.join("config", "storm-setup.yaml")) as f:
    return yaml.load(f.read())

if __name__ == "__main__":
  ipv4Addresses = docker_run.get_ipv4_addresses()
  stormConfig = get_storm_config()
  dockerHostname = None
  for supervisorConfig in stormConfig["storm.supervisor.hosts"]:
    if supervisorConfig["ip"] in ipv4Addresses:
      dockerHostname = supervisorConfig["aliases"][0]
  if dockerHostname is None:
    raise RuntimeError(re.sub("\s+", " ",
      """IP address of this machine does not match any IP address supplied in
      the `storm_supervisor_hosts` section of `config/storm-supervisor.yaml`.
      """).strip()
    )

  dockerRunArgs = docker_run.construct_docker_run_args(
    myIPv4Addresses=ipv4Addresses,
    # See the usage of this script at the top of the file... and you'll
    # understand why we need to subscript `sys.argv` from 2
    dockerRunArgv=sys.argv[2:],
  )
  # Check if any Zookeeper or Nimbus Docker container is running on this host.
  # If so, add links to those Docker containers.
  zookeeperLink = ""
  stormYamlConfig = stormConfig["storm.yaml"]
  if any([(myIpAddress in stormYamlConfig["storm.zookeeper.servers"])
      for myIpAddress in ipv4Addresses]):
    zookeeperLink = "--link zookeeper:zk"

  nimbusLink = ""
  if any([(myIpAddress == stormYamlConfig["nimbus.host"])
      for myIpAddress in ipv4Addresses]):
    nimbusLink = "--link nimbus:nimbus"
  dockerRunCmd = re.sub(r"""\s+""", " ",
    """docker run -h {docker_hostname} {zookeeper_link} {nimbus_link}
       {docker_run_args} --is-storm-supervisor""".format(
      docker_hostname=dockerHostname,
      zookeeper_link=zookeeperLink,
      nimbus_link=nimbusLink,
      docker_run_args=dockerRunArgs,
    )
  ).strip()
  print(dockerRunCmd)
  os.system(dockerRunCmd)
