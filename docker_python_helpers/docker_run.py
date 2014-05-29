# Executes the appropriate `docker run` command for different Storm components

import os
import os.path
import re
import subprocess
import sys
import yaml

def get_ipv4_addresses():
  """Returns all possible IPv4 addresses for the machine based on the output of
  the `ifconfig` command, excluding '127.0.0.1'.

  Returns:
    list of str: List of IPv4 addresses for this machine, excluding '127.0.0.1'.
  """
  p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
  out, _ = p.communicate()
  lines = out.split("\n")
  inetAddrRegex = re.compile(
    r"""^inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"""
  )
  ipAddresses = []
  for line in lines:
    line = line.strip()
    matchObj = inetAddrRegex.match(line)
    if matchObj is not None:
      ipAddresses.append(matchObj.group(1))
  # Get public IP address for Amazon EC2 instance.
  # From:
  #   http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html
  ec2GetIpProc = subprocess.Popen([
    "curl", "http://169.254.169.254/latest/meta-data/public-ipv4"
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ec2GetIpProcOut, _ = ec2GetIpProc.communicate()
  if ec2GetIpProc.returncode == 0:
    ec2PublicIp = ec2GetIpProcOut.strip()
    if re.match(r"""\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}""",
        ec2PublicIp) is not None:
      ipAddresses.append(ec2PublicIp)
  ipAddresses.remove('127.0.0.1')
  return ipAddresses

def get_storm_config():
  """Returns the hash defined by the `config/storm-setup.yaml` file."""
  with open(os.path.join("config", "storm-setup.yaml")) as f:
    return yaml.load(f.read())

def construct_docker_run_args(dockerRunArgv=sys.argv,
    stormConfig=get_storm_config(), myIPv4Addresses=get_ipv4_addresses()):
  """Returns a string containing arguments for `docker run`, assuming that the
  entrypoint of the Dockerfile is the `base-storm/run-supervisord.py` script.

  Args:
    dockerRunArgv(list of str, optional): Actual arguments to `docker run`
      (not to the entrypoint of the Dockerfile). Please DO NOT include
      `docker run` in this list.
    stormConfig(dict, optional): Dictionary containing details for
      `storm.yaml`. This should be the return value of the `get_storm_config`
      function.
    myIPv4Addresses(list of str, optional): List of IPv4 addresses of the
      current machine.

  Returns:
    str: String containing arguments for `docker run`, with the arguments in
      `dockerRunArgv` coming first, followed by the arguments to the
      `base-storm/run-supervisord.py` script.
  """
  dockerRunArgsTemplate = """
      {docker_run_argv}
      {storm_supervisor_hosts}
      {storm_zookeeper_servers}
      {storm_zookeeper_port}
      {nimbus_host}
      {nimbus_thrift_port}
      {drpc_servers}
      {drpc_port}
      {drpc_invocations_port}
      {my_ip_addresses}
  """

  stormSupervisorHosts = " ".join(["--storm-supervisor-host {}@{}".format(
    hostInfo["ip"], ",".join(hostInfo["aliases"])
  ) for hostInfo in stormConfig["storm_supervisor_hosts"]])
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
  myIpAddresses = " ".join(["--my-ip-address {}".format(myIpAddress)
    for myIpAddress in myIPv4Addresses
  ])

  # Fill in the placeholders for the `docker run` args template
  dockerRunArgsString = dockerRunArgsTemplate.format(
    docker_run_argv=" ".join(dockerRunArgv),
    storm_supervisor_hosts=stormSupervisorHosts,
    storm_zookeeper_servers=stormZookeeperServers,
    storm_zookeeper_port=stormZookeeperPort,
    nimbus_host=nimbusHost,
    nimbus_thrift_port=nimbusThriftPort,
    drpc_servers=drpcServers,
    drpc_port=drpcPort,
    drpc_invocations_port=drpcInvocationsPort,
    my_ip_addresses=myIpAddresses,
  )

  # strip unnecessary whitespace
  return re.sub(r"""\s+""", " ", dockerRunArgsString).strip()


# When run as a main program
if __name__ == "__main__":
  # This script is used like `python -m docker_python_helpers <ARGS>`, hence
  # the need for subscripting sys.argv from 2
  dockerRunArgsString = construct_docker_run_args(sys.argv[2:])
  dockerRunCmd = "docker run {}".format(dockerRunArgsString)
  print(dockerRunCmd)
  # execute `docker run` with the generated args
  os.system(dockerRunCmd)
