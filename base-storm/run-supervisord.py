#!/usr/bin/env python

import argparse
import os
import os.path
import re
import subprocess

STORM_HOME = os.environ["STORM_HOME"]

STORM_ZOOKEEPER_SERVERS_TEMPLATE = """
storm.zookeeper.servers:
{storm_zookeeper_servers}

storm.zookeeper.port: {storm_zookeeper_port}
"""

STORM_NIMBUS_TEMPLATE = """
nimbus.host: "{nimbus_host}"
nimbus.thrift.port: {nimbus_thrift_port}
"""

STORM_DRPC_TEMPLATE = """
drpc.servers:
{drpc_servers}

drpc_port: {drpc_port}
drpc_invocations_port: {drpc_invocations_port}
"""

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
parser.add_argument("--storm-supervisor-host", action="append",
  dest="storm_supervisor_hosts"
)
parser.add_argument("--storm-zookeeper-server", action="append",
  dest="storm_zookeeper_servers", type=str,
  help=re.sub(r"""\s+""", " ",
    """IP address for a single server in `storm.zookeeper.servers` in
       the `storm.yaml` file"""
  ).strip()
)
parser.add_argument("--storm-zookeeper-port",
  dest="storm_zookeeper_port", type=int,
  help="`storm.zookeeper.port` for storm.yaml"
)
parser.add_argument("--nimbus-host",
  dest="nimbus_host", type=str,
  help=re.sub(r"""\s+""", " ",
    """IP address for `nimbus.host` in the `storm.yaml` file"""
  ).strip()
)
parser.add_argument("--nimbus-thrift-port",
  dest="nimbus_thrift_port", type=int,
  help=re.sub(r"""\s+""", " ",
    """Port for `nimbus.thrift.port` in the `storm.yaml` file"""
  ).strip()
)
parser.add_argument("--drpc-server", action="append",
  dest="drpc_servers", type=str,
  help=re.sub(r"""\s+""", " ",
    """IP address for a single server in  `drpc.servers` in the
       `storm.yaml` file"""
  ).strip()
)
parser.add_argument("--drpc-port",
  dest="drpc_port", type=int,
  help=re.sub(r"""\s+""", " ",
    """Port for `drpc.port` in the `storm.yaml` file"""
  ).strip()
)
parser.add_argument("--drpc-invocations-port",
  dest="drpc_invocations_port", type=int,
  help=re.sub(r"""\s+""", " ",
    """Port for `drpc.invocations.port` in the `storm.yaml` file"""
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
    for stormSupervisorStr in parsedArgs.storm_supervisor_hosts:
      # Each arg is of this format:
      #
      #     ipaddress@alias1,alias2,alias3,...
      #
      # Eg.
      #
      #     10.0.0.2@host-name-one,host-name-two
      try:
        [ipAddress, commaSeparatedAliases] = stormSupervisorStr.split("@")
        aliasList = commaSeparatedAliases.split(",")
        if ipAddress not in myIpAddresses:
          f.write("{} {}\n".format(ipAddress, " ".join(aliasList)))
      except ValueError as e:
        pass

stormYamlTemplate = None
with open(os.path.join(STORM_HOME, "conf", "storm.yaml.sample"), "r") as f:
  stormYamlTemplate = f.read()

stormZookeeperServers = []
for zkServer in parsedArgs.storm_zookeeper_servers:
  if zkServer in myIpAddresses:
    # This server has a Zookeeper running.
    # We assume that the Zookeeper is running in a Docker container, and that
    # this Docker container we're in was run with a link to the Zookeeper
    # Docker container.
    # We use the IP address of the Zookeeper Docker container in place of its
    # global IP address.
    stormZookeeperServers.append(os.environ["ZK_PORT_2181_TCP_ADDR"])
  else:
    stormZookeeperServers.append(zkServer)

nimbusHost = ""
if parsedArgs.nimbus_host in myIpAddresses:
  # This server has a storm-nimbus running.
  # There are 2 possibilities:
  # 1. This Docker container is running storm-nimbus
  # 2. storm-nimbus is running on a separate Docker container on the same
  #    machine, and this Docker container was run with a link to the
  #    storm-nimbus Docker container.
  try:
    # To find out which case it is, we look for the `NIMBUS_PORT_6627_TCP_ADDR`
    # environment variable, which will be created if this Docker container was
    # run with a link to the storm-nimbus Docker container.
    nimbusHost = os.environ["NIMBUS_PORT_6627_TCP_ADDR"]
  except KeyError:
    # The `NIMBUS_PORT_6627_TCP_ADDR` environment variable does not exist, so
    # we assume that this is the storm-nimbus Docker container (hence it does
    # not have a link to itself), and use the output of `hostname -i` as the
    # nimbus host.
    p = subprocess.Popen(["hostname", "-i"], stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    out, _ = p.communicate()
    nimbusHost = out.strip()
else:
  # This server has no storm-nimbus running. We use the IP address supplied by
  # the `--nimbus-host` flag.
  nimbusHost = parsedArgs.nimbus_host

# Replace the appropriate sections of `storm.yaml` using parameters supplied
# on the command line
stormYamlTemplate = stormYamlTemplate \
  .replace("### zookeeper section ###",
    STORM_ZOOKEEPER_SERVERS_TEMPLATE.format(
      storm_zookeeper_servers="".join([
        '  - "{}"\n'.format(zkServer) for zkServer in stormZookeeperServers
      ]),
      storm_zookeeper_port=parsedArgs.storm_zookeeper_port,
    )
  ) \
  .replace("### nimbus section ###",
    STORM_NIMBUS_TEMPLATE.format(
      nimbus_host=nimbusHost,
      nimbus_thrift_port=parsedArgs.nimbus_thrift_port,
    )
  ) \
  .replace("### drpc section ###",
    STORM_DRPC_TEMPLATE.format(
      drpc_servers="".join([
        '  - "{}"\n'.format(drpcServer) for drpcServer in
          parsedArgs.drpc_servers
      ]),
      drpc_port=parsedArgs.drpc_port,
      drpc_invocations_port=parsedArgs.drpc_invocations_port,
    )
  )
with open(os.path.join(STORM_HOME, "conf", "storm.yaml"), "w") as f:
  f.write(stormYamlTemplate)

os.system("supervisord")
