from __future__ import print_function

import os.path

import yaml

def _print_fatal_and_exit(msg):
  print("FATAL: {}".format(msg), file=sys.stderr)
  sys.exit(1)

def _print_warning(msg):
  print("WARNING: {}".format(msg))

def _main():
  d = None
  storm_yaml_path = os.path.join("config", "storm-setup.yaml")
  if not os.path.exists(storm_yaml_path):
    print("Configuration file {} does not exist. Exiting.".format(
      storm_yaml_path
    ))
  with open(storm_yaml_path, "r") as f:
    d = yaml.load(f.read())
  if "servers" not in d:
    _print_fatal_and_exit("'servers' key not present")
  server_dict = d["servers"]
  for supervisor_host in d["storm.supervisor.hosts"]:
    if supervisor_host not in server_dict:
      _print_warning(
        "Host `{}` for 'storm.supervisor.hosts' not found in 'servers'".format(
          supervisor_host
        )
      )
  storm_yaml_conf = d["storm.yaml"]
  for zk_server in storm_yaml_conf["storm.zookeeper.servers"]:
    if zk_server not in server_dict:
      _print_warning(
        "Host `{}` for 'storm.zookeeper.servers' not found in 'servers'".format(
          zk_server
        )
      )
  if storm_yaml_conf["nimbus.host"] not in server_dict:
    _print_warning("Host `{}` for 'nimbus.host' not found in 'servers'".format(
      storm_yaml_conf["nimbus.host"]
    ))
  # TODO: Check for drpc server as well

if __name__ == "__main__":
  _main()
