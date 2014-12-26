# This script is used to run a Docker container with `storm-supervisor`.
# Usage:
#
#     python -m docker_python_helpers/run_storm_supervisor.py <ARGS>

import os
import os.path
import re
import subprocess
import sys
import yaml

from . import docker_run

if __name__ == "__main__":
  stormConfig = docker_run.get_storm_config()
  ipv4Addresses = docker_run.get_ipv4_addresses(
    stormConfig["is_localhost_setup"],
    stormConfig.get("all_machines_are_ec2_instances", False)
  )
  dockerHostname = None
  for supervisor_host in stormConfig["storm.supervisor.hosts"]:
    if stormConfig["servers"][supervisor_host] in ipv4Addresses:
      dockerHostname = "{}-supervisor".format(supervisor_host)
  if dockerHostname is None:
    raise RuntimeError(re.sub("\s+", " ",
      """IP address of this machine does not match any IP address supplied in
      the `storm_supervisor_hosts` section of `config/storm-supervisor.yaml`.
      """).strip()
    )

  dockerRunArgs = docker_run.construct_docker_run_args(
    # See the usage of this script at the top of the file... and you'll
    # understand why we need to subscript `sys.argv` from 2
    sys.argv[2:], ipv4Addresses
  )
  # construct appropriate port arguments for Storm supervisor and logviewer
  # since we run those 2 services in the `storm-supervisor` container
  dockerPortArgs = docker_run.construct_docker_run_port_args(["supervisor",
    "logviewer"
  ])

  # Check if any Zookeeper or Nimbus Docker container is running on this host.
  # If so, add links to those Docker containers.
  zookeeperLink = ""
  stormYamlConfig = stormConfig["storm.yaml"]
  zk_server_ips = [
    stormConfig["servers"][zk_server] for zk_server in
      stormYamlConfig["storm.zookeeper.servers"]
  ]
  if any([(myIpAddress in zk_server_ips) for myIpAddress in ipv4Addresses]):
    zookeeperLink = "--link zookeeper:zk"
  else:
    # check if zookeeper ambassador runs here.
    # We use a `docker ps | grep zk_ambassador`. Very crude but it should work.
    check_zk_amb_proc = subprocess.Popen(
      ["docker", "ps"], stdout=subprocess.PIPE
    )
    proc_output = b""
    try:
      proc_output = subprocess.check_output(
        ["grep", "zk_ambassador"], stdin=check_zk_amb_proc.stdout
      )
    except subprocess.CalledProcessError:
      pass
    check_zk_amb_proc.wait()
    if len(proc_output) > 0:
      zookeeperLink = "--link zk_ambassador:zk"

  nimbusLink = ""
  nimbus_ip_address = stormConfig["servers"][stormYamlConfig["nimbus.host"]]
  if any([(myIpAddress == nimbus_ip_address) for myIpAddress in ipv4Addresses]):
    nimbusLink = "--link nimbus:nimbus"
  dockerRunCmd = re.sub(r"""\s+""", " ",
    """docker run -h {docker_hostname} {zookeeper_link} {nimbus_link}
       {docker_port_args} {docker_run_args} --is-storm-supervisor""".format(
      docker_hostname=dockerHostname,
      zookeeper_link=zookeeperLink,
      nimbus_link=nimbusLink,
      docker_port_args=" ".join(dockerPortArgs),
      docker_run_args=dockerRunArgs,
    )
  ).strip()
  print(dockerRunCmd)
  os.system(dockerRunCmd)
