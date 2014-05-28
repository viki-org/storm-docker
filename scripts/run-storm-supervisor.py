# Runs the storm-supervisor

import os
import os.path
import re
import yaml

stormConfig = None
with open(os.path.join("config", "storm-supervisor.yaml")) as f:
  stormConfig = yaml.load(f.read())

dockerCmdTemplate = """
  docker run -h {docker_storm_supervisor_host_name}
    --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.4.4
    -p 49000:8000 -p 127.0.0.1:49022:22
    -p 6700:6700 -p 6701:6701 -p 6702:6702 -p 6703:6703
    --name supervisor
    {docker_links_for_host}
    -d viki_data/storm-supervisor
    {is_host}
    {external_hosts}
    {storm_zookeeper_servers}
    {storm_zookeeper_port}
    {nimbus_host}
    {nimbus_thrift_port}
    {drpc_servers}
    {drpc_port}
    {drpc_invocations_port}
"""

# Add links if we're running on the host machine
dockerLinksForHost = ""
isHostFlag = ""
if stormConfig["is_host"]:
  dockerLinksForHost = "--link nimbus:nimbus --link zookeeper:zk"
  isHostFlag = "--is-host"

externalHosts = ""
for hostInfo in stormConfig["external_hosts"]:
  externalHosts += " --external-host {}@{}".format(hostInfo["ip"],
    ",".join(hostInfo["aliases"])
  )

# Settings when `--is-host` is not set
stormZookeeperServers = ""
stormZookeeperPort = ""
nimbusHost = ""
nimbusThriftPort = ""
drpcServers = ""
drpcPort = ""
drpcInvocationsPort = ""
if isHostFlag == "":
  stormZookeeperServers = " ".join([
    "--storm-zookeeper-server {}".format(zkServer) for zkServer in
      stormConfig["storm.zookeeper.servers"]
  ])
  stormZookeeperPort = "--storm-zookeeper-port {}".format(
    stormConfig["storm.zookeeper.port"]
  )
  nimbusHost = "--nimbus-host {}".format(stormConfig["nimbus.host"])
  nimbusThriftPort = "--nimbus-thrift-port {}".format(
    stormConfig["nimbus.thrift.port"]
  )
  drpcServers = " ".join([
    "--drpc-server {}".format(drpcServer) for drpcServer in
      stormConfig["drpc.servers"]
  ])
  drpcPort = "--drpc-port {}".format(stormConfig["drpc.port"])
  drpcInvocationsPort = "--drpc-invocations-port {}".format(
    stormConfig["drpc.invocations.port"]
  )

# Fill in the values for the docker command template to generate the actual
# `docker run` command
dockerCmd = dockerCmdTemplate.format(
  docker_storm_supervisor_host_name=
    stormConfig["docker_storm_supervisor_host_name"],
  docker_links_for_host=dockerLinksForHost,
  is_host=isHostFlag,
  external_hosts=externalHosts,
  storm_zookeeper_servers=stormZookeeperServers,
  storm_zookeeper_port=stormZookeeperPort,
  nimbus_host=nimbusHost,
  nimbus_thrift_port=nimbusThriftPort,
  drpc_servers=drpcServers,
  drpc_port=drpcPort,
  drpc_invocations_port=drpcInvocationsPort
)

# strip unnecessary whitespace
dockerCmd = re.sub(r"""\s+""", " ", dockerCmd).strip()
print(dockerCmd)

os.system(dockerCmd)
