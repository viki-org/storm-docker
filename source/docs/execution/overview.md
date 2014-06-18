---
title: Execution Overview
---

Execution Overview
==================

The `start-storm.sh` script is used to run the appropriate Bash script in the
`scripts` folder. This can be one of:

- scripts/run-storm-docker-component.sh
- scripts/run-storm-supervisor.sh
- scripts/run-zookeeper.sh

The `run-storm-docker-component.sh` script is used to run either the
storm-nimbus or storm-ui Docker container. Use `scripts/run-storm-supervisor.sh`
for to run the storm-supervisor Docker and `scripts/run-zookeeper.sh` for the
zookeeper Docker.

In turn, each of the above bash scripts executes a Python script in the
`docker_python_helpers` folder to generate the `docker run` command and
arguments appropriate for it based on the `config/storm-setup.yaml` file.
The generated `docker run` command is printed out by the Python script.

As such, the Python scripts in the `docker_python_helpers` folder are one of
the pillars of this repository. Hackers should read the scripts here in detail,
along with the various `Dockerfile`s and their entrypoints (Python scripts too)
to gain a better understanding of this repository.
