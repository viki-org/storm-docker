from __future__ import print_function
from fabric.api import run, env, execute, task
from fabric.context_managers import cd

import argparse
import os.path
import sys

import yaml

parser = argparse.ArgumentParser(
  description="Remotely run the various Docker images in storm-docker"
)
parser.add_argument("--zk", "--zookeeper", action="store_true",
  dest="zookeeper", help="Run Zookeeper Docker images"
)
parser.add_argument("--supervisor", action="store_true",
  dest="supervisor", help="Run Storm supervisor Docker images"
)
parser.add_argument("--nimbus", action="store_true",
  dest="nimbus", help="Run Storm Nimbus Docker image"
)
parser.add_argument("--ui", action="store_true",
  dest="ui", help="Run Storm UI Docker image"
)
parser.add_argument("--all", action="store_true", dest="all",
  help="Run all available Docker images"
)

# Use settings in SSH config file
env.use_ssh_config = True

def _zk_and_nimbus_on_same_host(d):
  """Checks if the Nimbus Docker container runs on the same physical machine
  as some host that any Zookeeper Docker container runs on.

  d(dict): dictionary loaded from `storm-setup.yaml` file
  servers
  """
  servers = d["servers"]
  zk_server_list = d["storm.yaml"]["storm.zookeeper.servers"]
  zk_ip_addresses = [
    servers[zk_server] for zk_server in
      d["storm.yaml"]["storm.zookeeper.servers"]
  ]
  return servers[d["storm.yaml"]["nimbus.host"]] in zk_ip_addresses

def _main():
  yaml_file_path = os.path.join("config", "storm-setup.yaml")
  if not os.path.exists(yaml_file_path):
    print("{} does not exist. Exiting.".format(yaml_file_path), file=sys.stderr)
    sys.exit(1)
  with open(yaml_file_path, "r") as f:
    d = yaml.load(f.read())

  args = parser.parse_args()
  if args.all:
    args.zookeeper = args.nimbus = args.ui = args.supervisor = True

  need_ambassador = False
  if args.zookeeper or args.nimbus or args.ui:
    need_ambassador = not _zk_and_nimbus_on_same_host(d)

  if args.zookeeper:
    zk_server_list = d["storm.yaml"]["storm.zookeeper.servers"]
    if need_ambassador:
      # Launch ambassador along with zookeeper on the first zookeeper server
      # listed in `storm.yaml -> storm.zookeeper.servers` if the user wants to
      # run the Nimbus docker on a machine that is not running a Zookeeper server.
      execute(
        _run_docker_component, "zookeeper-with-ambassador",
        hosts=zk_server_list[:1]
      )
      execute(_run_docker_component, "zookeeper", hosts=zk_server_list[1:])
    else:
      # Nimbus Docker is on running on the same physical machine as some
      # Zookeeper docker. So we just run the Zookeeper docker(s) normally.
      execute(_run_docker_component, "zookeeper", hosts=zk_server_list)
  if args.nimbus:
    if need_ambassador:
      execute(
        _run_docker_component, "nimbus-with-zookeeper-ambassador",
        hosts=d["storm.yaml"]["nimbus.host"]
      )
    else:
      execute(
        _run_docker_component, "nimbus",
        hosts=d["storm.yaml"]["nimbus.host"]
      )
  if args.ui:
    if need_ambassador:
      execute(
        _run_docker_component, "ui-on-zk-ambassador-machine",
        hosts=d["storm.yaml"]["nimbus.host"]
      )
    else:
      execute(
        _run_docker_component, "ui", hosts=d["storm.yaml"]["nimbus.host"]
      )
  if args.supervisor:
    execute(
      _run_docker_component, "supervisor",
      hosts=d["storm.supervisor.hosts"]
    )

@task
def _run_docker_component(component):
  with cd("$HOME"):
    with cd("storm-docker"):
      run("./destroy-storm.sh {}".format(component), warn_only=True)
      run("./start-storm.sh {}".format(component))

if __name__ == "__main__":
  _main()
