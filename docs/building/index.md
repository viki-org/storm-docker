---
title: Building
---

Building
========

This page discusses the build process of storm-docker.

## Makefile

storm-docker makes use of GNU Make as our build tool. The build file is
_kind of_ messy, but its overall goal is to build / rebuild the various Docker
images in this repository.

We will be touching on various aspects of the Makefile in the sections below.

## Copying Configuration files to Docker folders

storm-docker requires the following configuration files to be present:

- `config/storm-setup.yaml`
- `config/cluster.xml`
- `config/zoo.cfg`

You should use the corresponding `.sample` files for the above configuration
files as a starting point. The sample configuration files contain comments with
detailed information on how you can go about filling the actual configuration
files.

For an initial start, you can copy the sample configuration files to "concrete"
configuration files (any existing concrete configuration files will not be
overwritten) using:

    ./copy-sample-config.sh

One of the major steps the `make` command does is to copy the configuration
files to their destination folders before the Dockerfiles are executed by the
Docker daemon. The `base-storm` and `zookeeper` Dockerfiles will add the
required configuration files to the built Docker image, which makes them
available to the running Docker containers.

Some advantages of adding the configuration files like this include:

- Allowing the user to perform very fine grained configuration of the Storm
cluster while providing a starting point through sample configuration files
- 
