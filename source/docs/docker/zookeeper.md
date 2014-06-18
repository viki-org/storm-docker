---
title: zookeeper Docker
---

zookeeper Docker
================

Dockerfile: `zookeeper/Dockerfile`

Entrypoint source file: `zookeeper/run-zookeeper.py`

The `zookeeper` Docker is used to run 1 instance of
[Zookeeper](http://zookeeper.apache.org/). Storm uses Zookeeper for
coordinating a cluster.

## Services Running in this Docker

- SSH daemon (accessible only from the machine running the Docker)
- Zookeeper

### SSH Daemon

The SSH daemon allows you to SSH into the `zookeeper` Docker and take a look at
what's going on. It was added due to the difficulty we faced in getting
Zookeeper to run on Docker.

The SSH daemon runs on port 22 of the Docker container and is mapped to port
49022 of the host machine.

To access it from the machine running the `zookeeper` Docker:

    ssh -p 49122 root@localhost

## Overview of Entrypoint

The entrypoint of the Zookeeper Docker is `zookeeper/run-zookeeper.py`
which does the following:

- checks that one of its IP addresses (supplied via the `--my-ip-address` flags
to `docker run`) is in the `storm-setup.yaml` file. Otherwise, an exception is
raised
- Adds the `clientPort` to the Zookeeper configuration file
- For a multiple Zookeeper setup, adds a `myid` file for this instance
corresponding to its `server.X` entry (described in the next point).
- For a multiple Zookeeper setup, appends the `server.X` entries to the
Zookeeper configuration file
- runs supervisord (which launches the services stated in the above section)

## Subtle points storm-docker takes care of

Before we carry on, below is a link to the **Clustered (Multi-Server) Setup**
section in the Zookeeper Administrator's Guide:

[http://zookeeper.apache.org/doc/r3.4.6/zookeeperAdmin.html#sc_zkMulitServerSetup](http://zookeeper.apache.org/doc/r3.4.6/zookeeperAdmin.html#sc_zkMulitServerSetup)

The `myid` file is probably used for each Zookeeper instance to identify itself
in the server.X entries and is easily missed out (refer to point 5 of the link
above). This is one of those subtle things that the storm-docker repository
takes care of.

For the `server.X` entries (refer to the Zookeeper's Administrator's Guide), the
IP address for the current Zookeeper's entry must be converted to the Docker's
IP address, otherwise the Zookeeper cluster will not be able to carry out
elections and Storm will not run. Once again, storm-docker takes care of that
for you.
