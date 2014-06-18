---
title: storm-ui
---

storm-ui Docker
===============

Dockerfile: `storm-ui/Dockerfile`

Entrypoint source file: `base-storm/run-supervisord.py`

## Services running in this Docker

- Storm UI

## Setup specific to storm-docker

In `start-storm.sh`, we can see the `--link nimbus:nimbus` and
`--link zookeeper:zk` flags passed to `scripts/run-storm-docker-component.sh`.
These flags are subsequently passed down to
`docker_python_helpers/docker_run.py` and eventually form part of the generated
`docker run` command for `storm-ui`.

As such, the `storm-ui` Docker in this repository links to a running
`storm-nimbus` Docker container and a running `zookeeper` Docker container.
Take note of that before running the `storm-ui` Docker container. You will need
to hack this repository if you do not want those Docker links to be made when
starting the `storm-ui` container; the necessary edits will not be difficult to
identify and correctly make.

## Additional Information

Storm UI gives you a web interface for viewing Storm settings (obtained from
Storm Nimbus), viewing running Storm toplogies, killing running Storm
topologies, etc. It is accessible using a web browser via the `ui.port`
supplied in the `config/storm-setup.yaml`, defaulting to port 8080.

For instance, if the global IP address of the machine running the `storm-ui`
Docker is `192.216.200.32` and `ui.port` is 8572, then the Storm UI is
accessible via `http://192.216.200.32:8572`.
