#!/usr/bin/env python

import argparse
import os
import os.path
import re
import subprocess
import yaml

STORM_HOME = os.environ["STORM_HOME"]

# Opens the `storm-setup.yaml` file added to this Docker container. The file was
# copied from the `config/storm-setup.yaml` file in the storm-docker repository
# during a `make` execution.
stormSetupConfig = None
with open(os.environ["STORM_SETUP_YAML"]) as f:
  stormSetupConfig = yaml.load(f.read())

parser = argparse.ArgumentParser(
  description="Configures and runs storm-supervisor"
)
parser.add_argument("--is-storm-supervisor", action="store_true", default=False,
  dest="is_storm_supervisor",
  help=re.sub(r"""\s+""", " ",
    """Supply this flag if this Docker container is running a
    storm-supervisor"""
  ).strip()
)
parser.add_argument("--my-ip-address", action="append",
  dest="my_ip_addresses", type=str,
  help=re.sub(r"""\s+""", " ",
    """IP address for the host machine"""
  ).strip()
)

parsedArgs = parser.parse_args()
myIpAddresses = parsedArgs.my_ip_addresses

# For a Docker container running a storm-supervisor.
# Add to `/etc/dnsmasq-extra-hosts` the storm-supervisor hosts whose
# IP addresses are not equal to that of this host machine
if parsedArgs.is_storm_supervisor:
  with open("/etc/dnsmasq-extra-hosts", "w") as f:
    stormSupervisorHosts = stormSetupConfig["storm.supervisor.hosts"]
    for supervisor_host in stormSupervisorHosts:
      ip_address = stormSetupConfig["servers"][supervisor_host]
      alias = "{}-supervisor".format(supervisor_host)
      if ip_address not in myIpAddresses:
        f.write("{} {}\n".format(ip_address, alias))

# This dict contains everything that should be written to the
# `$STORM_HOME/conf/storm.yaml` file
stormYamlConfig = stormSetupConfig["storm.yaml"]

# Build the storm.zookeeper.servers section of the `storm.yaml` file
# by replacing the SSH hostnames with actual IP addresses
storm_yaml_zk_servers_section = [
  stormSetupConfig["servers"][zk_server] for
    zk_server in stormYamlConfig["storm.zookeeper.servers"]
]

# We're gonna check if a Zookeeper runs on the server hosting our current
# Docker container.
#
# If that's the case, we assume that the Zookeeper is running in a Docker
# container, and that this Docker container we're in was run with a link to the
# Zookeeper Docker container.
# We use the IP address of the Zookeeper Docker container in place of its
# global IP address.
zk_server_ip_to_replace = None
# Loop through the Zookeeper server IP addresses
for zk_server_ip in storm_yaml_zk_servers_section:
  if zk_server_ip in myIpAddresses:
    # The server hosting our current Docker container has a Zookeeper running.
    zk_server_ip_to_replace = zk_server_ip
    break

# Zookeeper is running on the same server
if zk_server_ip_to_replace is not None:
  # Obtain the index of the Zookeeper IP address we're replacing
  idx = storm_yaml_zk_servers_section.index(zk_server_ip_to_replace)
  # Obtain the environment variable name for `storm.zookeeper.port` because
  # we allow the user to choose the port (so it is no longer the default 2181)
  zk_port_env_var = "ZK_PORT_{}_TCP_ADDR".format(
    stormYamlConfig["storm.zookeeper.port"]
  )
  storm_yaml_zk_servers_section.remove(zk_server_ip_to_replace)
  storm_yaml_zk_servers_section.insert(idx, os.environ[zk_port_env_var])

stormYamlConfig["storm.zookeeper.servers"] = storm_yaml_zk_servers_section

# We're gonna check if Storm Nimbus runs on the server hosting our current
# Docker container.
# If so, we can replace the globally accessible "nimbus.host" IP address with
# a "more efficient" IP address (the IP address of the Docker container running
# the Storm Nimbus).
if stormSetupConfig["servers"][stormYamlConfig["nimbus.host"]] in myIpAddresses:
  # This server has a Storm Nimbus running.
  # There are 2 possibilities:
  # 1. This Docker container is the one running the Storm Nimbus.
  # 2. Storm Nimbus is running on a separate Docker container on the same
  #    machine, and this Docker container was run with a link to the
  #    Storm Nimbus Docker container.
  try:
    # To determine if it's case number 2, we look for an environment variable
    # named `NIMBUS_PORT_{XYZ}_TCP_ADDR` where XYZ is the `nimbus.thrift.port`.
    # We first construct the name of this environment variable.
    nimbusEnvVar = "NIMBUS_PORT_{}_TCP_ADDR".format(
      stormYamlConfig["nimbus.thrift.port"]
    )
    # If this Docker container was run with a link to the Storm Nimbus Docker
    # container, then the environment variable will be present, and its value
    # is the IP address of the Storm Nimbus Docker container.
    # We set `nimbus.host` to that value.
    stormYamlConfig["nimbus.host"] = os.environ[nimbusEnvVar]
  except KeyError:
    # The `NIMBUS_PORT_{XYZ}_TCP_ADDR` environment variable does not exist
    # (there is no Docker link to the Storm Nimbus container), yet the
    # `nimbus.host` global IP address is one of the IP addresses of this
    # server.
    # We assume that this is case 1, and replace the IP address of
    # `nimbus.host` with the output of `hostname -i`.
    p = subprocess.Popen(["hostname", "-i"], stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    out, _ = p.communicate()
    stormYamlConfig["nimbus.host"] = out.strip()
else:
  # Storm Nimbus not running on the same physical machine.
  # But we have to replace the hostname with the IP address from the server list
  stormYamlConfig["nimbus.host"] = \
    stormSetupConfig["servers"][stormYamlConfig["nimbus.host"]]

# Write out to `$STORM_HOME/conf/storm.yaml`
with open(os.path.join(STORM_HOME, "conf", "storm.yaml"), "w") as f:
  f.write(yaml.dump(stormYamlConfig, default_flow_style=False))

os.system("supervisord")
