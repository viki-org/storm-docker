# Executes the appropriate `docker run` command for different Storm components

import os
import re
import subprocess
import sys

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
