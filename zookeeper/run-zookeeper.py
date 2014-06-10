#!/usr/bin/env python

import argparse
import os
import os.path
import re
import subprocess
import yaml

# `storm-setup.yaml` file we added
STORM_SETUP_YAML = os.environ["STORM_SETUP_YAML"]

# Zookeeper configuration file
ZK_CFG = os.environ["ZK_CFG"]

# Zookeeper `dataDir`
ZK_DATADIR = os.environ["ZK_DATADIR"]

# Opens the `storm-setup.yaml` file added to this Docker container. The file was
# copied from the `config/storm-setup.yaml` file in the storm-docker repository
# during a `make` execution.
stormSetupConfig = None
with open(STORM_SETUP_YAML, "r") as f:
  stormSetupConfig = yaml.load(f.read())

parser = argparse.ArgumentParser(
  description="Configures and runs Zookeeper"
)
parser.add_argument("--my-ip-address", action="append",
  dest="my_ip_addresses", type=str,
  help=re.sub(r"""\s+""", " ",
    """IP address for the host machine"""
  ).strip()
)

parsedArgs = parser.parse_args()

# IP addresses supplied in the `docker run` command
myIpAddresses = parsedArgs.my_ip_addresses

# Get list of Zookeeper servers from the STORM_SETUP_YAML file
zkIpAddresses = stormSetupConfig["storm.yaml"]["storm.zookeeper.servers"]

# Check the index of the current Zookeeper server.
# While this is only truly absolutely necessary for a multiple Zookeeper setup,
# we want to determine if the current server is one of the Zookeeper servers
# supplied in the $STORM_SETUP_YAML file.
myId = None
for myIpAddr in myIpAddresses:
  try:
    idx = zkIpAddresses.index(myIpAddr)
    myId = idx
  except ValueError:
    pass

if myId is None:
  # We do not see this server inside the $STORM_SETUP_YAML file. Error out.
  raise RuntimeError(re.sub(r"""\s+""", " ", """None of the supplied IP
    addresses (via --my-ip-address) are in the
    `storm.yaml` -> `storm.zookeeper.servers` section of the file `{}`
    """.format(STORM_SETUP_YAML)
  ))

# Add `clientPort` to the Zookeeper configuration file at this point, because
# we allow the user to change the `storm.zookeeper.port`
with open(ZK_CFG, "a") as f:
  f.write("clientPort={}\n".format(
    stormSetupConfig["storm.yaml"]["storm.zookeeper.port"]
  ))

# Differentiate between a multiple and single Zookeeper setup
if len(zkIpAddresses) > 1:
  # A multiple Zookeeper setup requires a `myid` file in the dataDir (whose
  # path is stored in the `ZK_DATADIR` environment variable).
  # This file contains a single line, which is a unique integer from 1 to 255
  # identifying the current Zookeeper.
  #
  # Write id to $ZK_DATADIR/myid
  with open(os.path.join(ZK_DATADIR, "myid"), "w") as f:
    f.write("{}\n".format(myId + 1))

  # The Docker container has its own IP address. We will need to obtain this
  # Docker IP address and substitute it in place of the IP address of this
  # host machine in the $ZK_CFG file later on.
  #
  # If we do not use the Docker IP address, Zookeeper will not properly bind to
  # the election port (normally 3888 by convention).
  proc = subprocess.Popen(["hostname", "-i"], stdout=subprocess.PIPE)
  dockerIp, _ = proc.communicate()
  dockerIp = dockerIp.strip()

  # Obtain the Zookeeper follower and election ports
  zkFollowerPort = stormSetupConfig["zookeeper.multiple.setup"]["follower.port"]
  zkElectionPort = stormSetupConfig["zookeeper.multiple.setup"]["election.port"]

  # Append the list of Zookeeper IP addresses to $ZK_CFG file
  with open(ZK_CFG, "a") as f:
    for (idx, zkIpAddr) in enumerate(zkIpAddresses):
      if idx == myId:
        # This is the entry for the current server. We use the Docker IP address
        # in place of the host IP address.
        f.write("server.{}={}:{}:{}\n".format(idx + 1, dockerIp, zkFollowerPort,
          zkElectionPort
        ))
      else:
        # Zookeeper entry for another server. Use its original IP address.
        f.write("server.{}={}:{}:{}\n".format(idx + 1, zkIpAddr, zkFollowerPort,
          zkElectionPort
        ))

# Start supervisord
os.system("supervisord")
