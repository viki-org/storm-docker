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

# Use settings in SSH config file
env.use_ssh_config = True

def _main():
  yaml_file_path = os.path.join("config", "storm-setup.yaml")
  if not os.path.exists(yaml_file_path):
    print("{} does not exist. Exiting.".format(yaml_file_path), file=sys.stderr)
    sys.exit(1)
  with open(yaml_file_path, "r") as f:
    d = yaml.load(f.read())
  args = parser.parse_args()
  if args.zookeeper:
    zk_server_list = d["storm.yaml"]["storm.zookeeper.servers"]
    execute(_run_zookeeper_docker, hosts=zk_server_list)

@task
def _run_zookeeper_docker():
  with cd("$HOME"):
    with cd("storm-docker"):
      run("./destroy-storm.sh zookeeper")
      run("./start-storm.sh zookeeper")

if __name__ == "__main__":
  _main()
