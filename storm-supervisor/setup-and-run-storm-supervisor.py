#!/usr/bin/env python

import argparse
import os
import re

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

parsedArgs = parser.parse_args()

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

os.system("supervisord")
