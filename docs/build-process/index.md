---
title: Build Process
---

Build Process
=============

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
required configuration files to the Docker image being built, which makes the
configuration files available to the running Docker containers.

By doing so, we allow the user to perform very fine grained configuration of
the Storm cluster using the sample configuration files as a starting point.

### Micro Optimization for copying configuration files

Whenever Docker encounters an `ADD` instruction in a Dockerfile, it checks the
timestamp of the file being added to determine whether it can make use of its
cache (this is just a guess).

Because of this, even if we override a configuration file in say the
`base-storm` folder with a configuration file with the exact same contents from
the `config` folder, Docker will treat the overriden file as new even though
the contents are unchanged.
Hence, on a new `docker build`, when Docker reaches the step of `ADD`ing the
configuration file, it will not make use of the cache and repeats the steps
after the `ADD` instruction, which can be very time consuming.

storm-docker solves this problem by only performing a copy of a configuration
file from the `config` folder to a destination folder on any one of the
following conditions:

- the destination configuration file does not exist
(eg. `config/storm-setup.yaml` has not been copied to
`base-storm/storm-setup.yaml`)
- the destination configuration file exists, but its contents differ from the
same file in the `config` folder. In this case, the configuration file in the
`config` folder is copied to the destination folder.

Hence, the configuration files are only copied when necessary.
Doing so allows Docker to make use of the cache as much as possible.
Not surprisingly, the code needed to perform this "conditional copying" takes
up the bulk of the complexity of our `Makefile`.

## docker build

The default goal of the `Makefile` is the `build-storm-docker-containers` rule.
Within the body of the goal are several `docker build` commands like the
following:

    docker build -t="viki_data/storm-nimbus" storm-nimbus

The default goal has prerequisites which build other Docker images. Ultimately,
things boil down to executing `docker build` commands for the Docker images
prescribed by `Dockerfile`s in this repository.
