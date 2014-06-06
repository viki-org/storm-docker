# Executes the appropriate `docker run` command for different Storm components

import argparse
import os
import re
import subprocess
import sys
import yaml

NIMBUS_THRIFT_PORT_STR = "nimbus.thrift.port"
DRPC_PORT_STR = "drpc.port"
DRPC_INVOCATIONS_PORT_STR = "drpc.invocations.port"
UI_PORT_STR = "ui.port"

STORM_DEFAULT_PORTS = {
  NIMBUS_THRIFT_PORT_STR: 6627,
  DRPC_PORT_STR: 3772,
  DRPC_INVOCATIONS_PORT_STR: 3773,
  UI_PORT_STR: 8080,
}

STORM_COMPONENT_PORTS = {
  "nimbus": [NIMBUS_THRIFT_PORT_STR, DRPC_PORT_STR, DRPC_INVOCATIONS_PORT_STR],
  "ui": [UI_PORT_STR],
}

parser = argparse.ArgumentParser(
  description="Generates the docker run command for the given Storm component",
  # The `-h` flag is in some args passed to this program to specify the Docker
  # hostname and will trigger this parser's help.
  # We disable the help flags here to ensure that it does not happen.
  add_help=False,
)
parser.add_argument("--storm-docker-component",
  choices=["nimbus", "ui"],
  dest="storm_component",
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
  return ipAddresses

def construct_docker_run_args(dockerRunArgv,
    myIPv4Addresses=get_ipv4_addresses()):
  """Returns a string containing arguments for `docker run`, assuming that the
  entrypoint of the Dockerfile is the `base-storm/run-supervisord.py` script.

  Args:
    dockerRunArgv(list of str, optional): Actual arguments to `docker run`
      (not to the entrypoint of the Dockerfile). Please DO NOT include
      `docker run` in this list.
    myIPv4Addresses(list of str, optional): List of IPv4 addresses of the
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

def construct_docker_run_port_args(portKeyStringList):
  """Constructs the arguments used by `docker run` for port forwarding and
  exposing ports.

  Args:
    portKeyStringList(list of str): List of strings (keys of the
      `STORM_DEFAULT_PORTS` dict)

  Returns:
    list of str: List of arguments to `docker run` for port forwarding and
      exposing ports
  """
  stormConfig = get_storm_config()
  stormYamlConfig = stormConfig["storm.yaml"]
  portForwardArgs = []
  portExposeArgs = []
  for portKeyString in portKeyStringList:
    portNum = stormYamlConfig.get(portKeyString,
      STORM_DEFAULT_PORTS[portKeyString]
    )
    portForwardArgs.append("-p {}:{}".format(portNum, portNum))
    portExposeArgs.append("--expose {}".format(portNum))
  return portForwardArgs + portExposeArgs

# When run as a main program
if __name__ == "__main__":
  # This script is used like `python -m docker_python_helpers <ARGS>`, hence
  # the need for subscripting sys.argv from 2
  parsedArgs, remArgList = parser.parse_known_args(args=sys.argv[2:])

  # Construct port forwarding command line args. These port forwarding args are
  # added here to allow users to choose the Docker and host ports to use in the
  # `config/storm-setup.yaml` file
  portArgs = construct_docker_run_port_args(
    STORM_COMPONENT_PORTS[parsedArgs.storm_component]
  )
  # Prepend port forwarding args to args list
  remArgList[:0] = portArgs

  dockerRunArgsString = construct_docker_run_args(remArgList)
  dockerRunCmd = "docker run {}".format(dockerRunArgsString)
  print(dockerRunCmd)
  # execute `docker run` with the generated args
  os.system(dockerRunCmd)
