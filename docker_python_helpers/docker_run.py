# Executes the appropriate `docker run` command for different Storm components

import argparse
import os
import re
import subprocess
import sys
import yaml

# Strings of sections specifying ports in `storm.yaml` for major Storm
# components
NIMBUS_THRIFT_PORT_STR = "nimbus.thrift.port"
DRPC_PORT_STR = "drpc.port"
DRPC_INVOCATIONS_PORT_STR = "drpc.invocations.port"
LOGVIEWER_PORT_STR = "logviewer.port"
UI_PORT_STR = "ui.port"
SUPERVISOR_SLOTS_PORTS_STR = "supervisor.slots.ports"
ZOOKEEPER_PORT_STR = "storm.zookeeper.port"
ZOOKEEPER_FOLLOWER_PORT_STR = "follower.port"
ZOOKEEPER_ELECTION_PORT_STR = "election.port"

class StormPort:
  """Information on a port type for a Storm component."""
  def __init__(self, ports, needsUDP=False, section="storm.yaml"):
    """Constructor for StormPort

    Args:
      ports(str or list of str): A single integer port or a list of integer
        ports for the port type
      needsUDP(bool, optional): Whether the port(s) should accept UDP traffic
      section(str, optional): The appropriate section in the
        `config/storm-setup.yaml` file for retrieving this port
    """
    # To simplify things, for the case where `tmpPorts` is a single integer
    # port, we convert it to a singleton list containing that port
    tmpPorts = ports
    if not isinstance(tmpPorts, list):
      tmpPorts = [tmpPorts]
    self._portList = tmpPorts
    self._needsUDP = needsUDP
    self._section = section

  @property
  def portList(self):
    return self._portList

  @property
  def needsUDP(self):
    return self._needsUDP

  @property
  def section(self):
    return self._section

# Default port(s) for a section in `storm.yaml`
STORM_DEFAULT_PORTS = {
  NIMBUS_THRIFT_PORT_STR:      StormPort(6627),
  DRPC_PORT_STR:               StormPort(3772),
  DRPC_INVOCATIONS_PORT_STR:   StormPort(3773),
  LOGVIEWER_PORT_STR:          StormPort(8000),
  UI_PORT_STR:                 StormPort(8080),
  SUPERVISOR_SLOTS_PORTS_STR:  StormPort([6700, 6701, 6702, 6703]),
  ZOOKEEPER_PORT_STR:          StormPort(2181),
  ZOOKEEPER_FOLLOWER_PORT_STR: StormPort(2888, needsUDP=True,
                                         section="zookeeper.multiple.setup"),
  ZOOKEEPER_ELECTION_PORT_STR: StormPort(3888,
                                         section="zookeeper.multiple.setup"),
}

# Dict of Storm component -> list of sections in `storm.yaml` specifying ports
STORM_COMPONENT_PORTS = {
  "drpc":       [DRPC_PORT_STR, DRPC_INVOCATIONS_PORT_STR],
  "logviewer":  [LOGVIEWER_PORT_STR],
  "nimbus":     [NIMBUS_THRIFT_PORT_STR],
  "supervisor": [SUPERVISOR_SLOTS_PORTS_STR],
  "ui":         [UI_PORT_STR],
  "zookeeper":  [ZOOKEEPER_PORT_STR, ZOOKEEPER_FOLLOWER_PORT_STR,
                 ZOOKEEPER_ELECTION_PORT_STR],
}

parser = argparse.ArgumentParser(
  description="Generates the docker run command for the given Storm component",
  # The `-h` flag is in some args passed to this program to specify the Docker
  # hostname and will trigger this parser's help.
  # We disable the help flags here to ensure that it does not happen.
  add_help=False,
)
parser.add_argument("--storm-docker-component",
  action="append",
  choices=["drpc", "nimbus", "supervisor", "ui"],
  dest="storm_components",
  help="The Storm component to run",
)

def get_storm_config():
  """Returns the Dict defined by the `config/storm-setup.yaml` file.

  Returns:
    Dict: the Dict defined by the `config/storm-setup.yaml` file."""
  with open(os.path.join("config", "storm-setup.yaml")) as f:
    return yaml.load(f.read())

def ec2_get_ip(public=True):
  """Returns the public or private IP address for the current EC2 machine.

  For the urls being queried, see:

      http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html

  Args:
    public(bool, optional): defaults to True. If True, the public IP of the
      EC2 machine is returned. If False, the private IP of the EC2 machine is
      returned.

  Returns:
    str: Public or private IP address for the current EC2 machine
  """
  urlToQuery = None
  if public:
    urlToQuery = "http://169.254.169.254/latest/meta-data/public-ipv4"
  else:
    urlToQuery = "http://169.254.169.254/latest/meta-data/local-ipv4"
  getIpProc = subprocess.Popen(["curl", urlToQuery, "--connect-timeout", "10"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
  )
  procOut, _ = getIpProc.communicate()
  if getIpProc.returncode == 0:
    mbIpAddr = procOut.strip()
    if re.match(r"""^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$""", mbIpAddr) \
        is not None:
      return mbIpAddr
    else:
      raise ValueError(
        "Return value of `{}` \"{}\" does not look like an IP address".format(
          "curl {}".format(urlToQuery), mbIpAddr
        )
      )
  else:
    # Most probably this server is not an EC2 instance
    return None

def get_ipv4_addresses(isLocalhostSetup=False,
    allMachinesAreEC2Instances=False):
  """Returns all possible IPv4 addresses for the machine based on the output of
  the `ifconfig` command. `127.0.0.1` will be included if True is supplied for
  the `isLocalhostSetup` parameter, it will be excluded otherwise.

  Args:
    isLocalhostSetup(bool, optional): Set this to True if you are running
      everything on one machine using 127.0.0.1 as the IP address

  Returns:
    list of str: List of IPv4 addresses for this machine
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
  if allMachinesAreEC2Instances:
    ec2PublicIp = ec2_get_ip(public=True)
    if ec2PublicIp is not None:
      ipAddresses.append(ec2PublicIp)
    ec2PrivateIp = ec2_get_ip(public=False)
    if ec2PrivateIp is not None:
      ipAddresses.append(ec2PrivateIp)
  try:
    ipAddresses.remove('127.0.0.1')
  except ValueError:
    pass
  if isLocalhostSetup:
    ipAddresses.append('127.0.0.1')
  return ipAddresses

def construct_docker_run_args(dockerRunArgv, myIPv4Addresses):
  """Returns a string containing arguments for `docker run`, assuming that the
  entrypoint of the Dockerfile is the `base-storm/run-supervisord.py` script.

  Args:
    dockerRunArgv(list of str, optional): Actual arguments to `docker run`
      (not to the entrypoint of the Dockerfile). Please DO NOT include
      `docker run` in this list.
    myIPv4Addresses(list of str): List of IPv4 addresses of the
      current machine.

  Returns:
    str: String containing arguments for `docker run`, with the arguments in
      `dockerRunArgv` coming first, followed by the arguments to the
      `base-storm/run-supervisord.py` script.
  """
  dockerRunArgsTemplate = """
      {docker_run_argv}
      {my_ip_addresses}
  """
  myIpAddresses = " ".join(["--my-ip-address {}".format(myIpAddress)
    for myIpAddress in myIPv4Addresses
  ])
  # Fill in the placeholders for the `docker run` args template
  dockerRunArgsString = dockerRunArgsTemplate.format(
    docker_run_argv=" ".join(dockerRunArgv),
    my_ip_addresses=myIpAddresses,
  )
  # strip unnecessary whitespace
  return re.sub(r"""\s+""", " ", dockerRunArgsString).strip()

def construct_docker_run_port_args(stormComponentList):
  """Constructs the arguments used by `docker run` for port forwarding and
  exposing ports.

  Args:
    stormComponentList(list of str): List of strings, each of which is a Storm
      component

  Returns:
    list of str: List of arguments to `docker run` for port forwarding and
      exposing ports
  """
  stormConfig = get_storm_config()
  portForwardArgs = []
  portExposeArgs = []

  # For each Storm component
  for stormComponent in stormComponentList:
    # We retrieve the list of string keys for sections in
    # `config/storm-setup.yaml` that specifies a configurable port / list of
    # ports
    portKeyStringsList = STORM_COMPONENT_PORTS[stormComponent]
    # For each section
    for portKeyString in portKeyStringsList:
      # Retrieve the `StormPort` object in `STORM_DEFAULT_PORTS`
      stormPortObj = STORM_DEFAULT_PORTS[portKeyString]
      # Retrieve the appropriate section in `config/storm-setup.yaml`
      # containing the port configuration
      stormYamlSection = stormConfig[stormPortObj.section]
      # Retrieve the port / list of ports for this section. Fallback to using
      # the default port / ports if the user did not specify any.
      portNumOrList = stormYamlSection.get(portKeyString, stormPortObj.portList)
      # To simplify things, for the case where `portNumOrList` is a single
      # port, we convert the single port into a singleton list containing that
      # port.
      if isinstance(portNumOrList, int):
        portNumOrList = [portNumOrList]
      for portNum in portNumOrList:
        # For each port, construct the port forwarding and expose args for
        # `docker run`
        portForwardArgs.append("-p {}:{}".format(portNum, portNum))
        # For port(s) that need to accept UDP traffic, we add another flag to
        # indicate it
        if stormPortObj.needsUDP:
          portForwardArgs.append("-p {}:{}/udp".format(portNum, portNum))
        portExposeArgs.append("--expose {}".format(portNum))
  return portForwardArgs + portExposeArgs

def main(args=None):
  if args is None:
    # No args provided, so this script is run as a main program.
    # This script is used like `python -m docker_python_helpers <ARGS>`, hence
    # the need for subscripting sys.argv from 2
    args = sys.argv[2:]

  parsedArgs, remArgList = parser.parse_known_args(args)

  # Construct port forwarding command line args. These port forwarding args are
  # added here to allow users to choose the Docker and host ports to use in the
  # `config/storm-setup.yaml` file
  portArgs = construct_docker_run_port_args(parsedArgs.storm_components)

  # Prepend port forwarding args to args list
  remArgList[:0] = portArgs

  stormConfig = get_storm_config()
  ipv4Addresses = get_ipv4_addresses(stormConfig["is_localhost_setup"],
    stormConfig.get("all_machines_are_ec2_instances", False)
  )
  dockerRunArgsString = construct_docker_run_args(remArgList, ipv4Addresses)
  dockerRunCmd = "docker run {}".format(dockerRunArgsString)
  print(dockerRunCmd)
  # execute `docker run` with the generated args
  os.system(dockerRunCmd)

# When run as a main program
if __name__ == "__main__":
  main()
