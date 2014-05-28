#!/usr/bin/env python

import argparse
import os
import os.path
import re

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

parser.add_argument("--is-host", action="store_true", default=False,
  dest="is_host",
  help=re.sub(r"""\s+""", " ",
    """Supply this if the storm-supervisor is running on the host machine
       (on top of zookeeper, storm nimbus, storm ui)"""
  ).strip()
)
parser.add_argument("--external-host", action="append",
  dest="external_hosts"
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

parsedArgs = parser.parse_args()
print(parsedArgs)

# Parse the external hosts and add them into /etc/dnsmasq-extra-hosts
if parsedArgs.external_hosts:
  with open("/etc/dnsmasq-extra-hosts", "w") as f:
    for externalHostArg in parsedArgs.external_hosts:
      # Each arg is of this format:
      #
      #     ipaddress@alias1,alias2,alias3,...
      #
      # Eg.
      #
      #     10.0.0.2@host-name-one,host-name-two
      try:
        [ipAddress, commaSeparatedAliases] = externalHostArg.split("@")
        aliasList = commaSeparatedAliases.split(",")
        f.write("{} {}\n".format(ipAddress, " ".join(aliasList)))
      except ValueError as e:
        pass

# substitute the "%zookeper%" and "%nimbus%" strings if running on host
if parsedArgs.is_host:
  os.system(re.sub(r"""\s+""", " ",
    '''sed -i -e "s/%zookeeper%/$ZK_PORT_2181_TCP_ADDR/g"
       $STORM_HOME/conf/storm.yaml'''
  ).strip())
  os.system(re.sub(r"""\s+""", " ",
    '''sed -i -e "s/%nimbus%/$NIMBUS_PORT_6627_TCP_ADDR/g"
       $STORM_HOME/conf/storm.yaml'''
  ).strip())
else:
  stormYamlTemplate = None
  with open(os.path.join(STORM_HOME, "conf", "storm.yaml.sample"), "r") as f:
    stormYamlTemplate = f.read()
  # Replace the appropriate sections of `storm.yaml` using parameters supplied
  # on the command line
  stormYamlTemplate = stormYamlTemplate \
    .replace("### zookeeper section ###",
      STORM_ZOOKEEPER_SERVERS_TEMPLATE.format(
        storm_zookeeper_servers="".join([
          '  - "{}"\n'.format(zkServer) for zkServer in
            parsedArgs.storm_zookeeper_servers
        ]),
        storm_zookeeper_port=parsedArgs.storm_zookeeper_port,
      )
    ) \
    .replace("### nimbus section ###",
      STORM_NIMBUS_TEMPLATE.format(
        nimbus_host=parsedArgs.nimbus_host,
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
