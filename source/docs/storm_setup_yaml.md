---
title: storm-setup.yaml Configuration
---

storm-setup.yaml Configuration
==============================

The `config/storm-setup.yaml` file is the most important file in the
storm-docker repository, and the one that you have to customize to make things
work. You should use the `config/storm-setup.yaml.sample` file as the
starting point for the `config/storm-setup.yaml` file.

The `config/storm-setup.yaml.sample` file contains rather detailed documentation
on how to fill up the actual `storm-setup.yaml` file. This page serves to
illuminate some of the more uncertain points about some keys in the file.

**NOTE:** This file may be merged into `config/storm-setup.yaml.sample` in the
future.

## storm.supervisor.hosts

Each entry represents a single storm-supervisor Docker instance. For an alias,
you can use any string valid for a hostname, as long as it is unique.
The aliases are used by the Storm Supervisor instances to identify one another
(Storm Supervisor does not use IP addresses for this).

## zookeeper.multiple.setup

As stated in the `config/storm-setup.yaml.sample`, this is only required for a
multiple server Zookeeper setup. Setups using a single Zookeeper can ignore this
section.

Election takes place among Zookeeper nodes for a multiple Zookeeper setup and
makes use of 2 additional ports on top of the `clientPort` - one for followers
to connect to the leader, the other for elections only.

## storm.yaml

Place exactly what you want for your Storm cluster's configuration under this
key.
