# Executes the appropriate `docker run` command for different Storm components

import os
import re
import subprocess
import sys
import yaml

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

def construct_docker_run_args(dockerRunArgv=sys.argv,
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


# When run as a main program
if __name__ == "__main__":
  # This script is used like `python -m docker_python_helpers <ARGS>`, hence
  # the need for subscripting sys.argv from 2
  dockerRunArgsString = construct_docker_run_args(sys.argv[2:])
  dockerRunCmd = "docker run {}".format(dockerRunArgsString)
  print(dockerRunCmd)
  # execute `docker run` with the generated args
  os.system(dockerRunCmd)
