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
    for stormSupervisorConfig in stormSupervisorHosts:
      ipAddress = stormSupervisorConfig["ip"]
      aliasList = stormSupervisorConfig["aliases"]
      if ipAddress not in myIpAddresses:
        f.write("{} {}\n".format(ipAddress, " ".join(aliasList)))

# This dict contains everything that should be written to the
# `$STORM_HOME/conf/storm.yaml` file
stormYamlConfig = stormSetupConfig["storm.yaml"]

# We're gonna check if a Zookeeper runs on the server hosting our current
# Docker container.
#
# If that's the case, we assume that the Zookeeper is running in a Docker
# container, and that this Docker container we're in was run with a link to the
# Zookeeper Docker container.
# We use the IP address of the Zookeeper Docker container in place of its
# global IP address.
zkServerIpToReplace = None
# Loop through the Zookeeper server IP addresses
for zkServer in stormYamlConfig["storm.zookeeper.servers"]:
  if zkServer in myIpAddresses:
    # The server hosting our current Docker container has a Zookeeper running.
    zkServerIpToReplace = zkServer
    break

# Zookeeper is running on the same server
if zkServerIpToReplace is not None:
  # Replace the IP address
  stormYamlConfig["storm.zookeeper.servers"].remove(zkServerIpToReplace)
  stormYamlConfig["storm.zookeeper.servers"].append(
    os.environ["ZK_PORT_2181_TCP_ADDR"]
  )

# We're gonna check if Storm Nimbus runs on the server hosting our current
# Docker container.
# If so, we can replace the globally accessible "nimbus.host" IP address with
# a "more efficient" IP address (the IP address of the Docker container running
# the Storm Nimbus).
if stormYamlConfig["nimbus.host"] in myIpAddresses:
  # This server has a Storm Nimbus running.
  # There are 2 possibilities:
  # 1. This Docker container is the one running the Storm Nimbus.
  # 2. Storm Nimbus is running on a separate Docker container on the same
  #    machine, and this Docker container was run with a link to the
  #    Storm Nimbus Docker container.
  try:
    # To determine if it's case number 2, we look for the
    # `NIMBUS_PORT_6627_TCP_ADDR` environment variable, which will be created
    # if this Docker container was run with a link to the Storm Nimbus Docker
    # container.
    stormYamlConfig["nimbus.host"] = os.environ["NIMBUS_PORT_6627_TCP_ADDR"]
  except KeyError:
    # The `NIMBUS_PORT_6627_TCP_ADDR` environment variable does not exist
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

# Write out to `$STORM_HOME/conf/storm.yaml`
with open(os.path.join(STORM_HOME, "conf", "storm.yaml"), "w") as f:
  f.write(yaml.dump(stormYamlConfig, default_flow_style=False))

os.system("supervisord")
