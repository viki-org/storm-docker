storm-docker
============

This repository is forked from https://github.com/wurstmeister/storm-docker
and contains some edits that are specific to running the
[storm-alerts](https://github.com/viki-org/storm-alerts) repository.

At Viki, we run the [Docker](https://www.docker.io/) images built from this
repository to obtain configured environments for the following components of the
[Storm 'alerts' topology](https://github.com/viki-org/storm-alerts):

- Zookeeper
- Nimbus
- Storm UI
- Storm Supervisor

By leveraging the power of [Docker](https://www.docker.io/) to create containers
on heterogeneous Linux servers and run on all of them as if they were
homogenous, the rather tedious process of:

- setting up Zookeeper
- setting up Nimbus
- setting up Storm UI
- setting up Storm Supervisor
- deploying storm-alerts and **hoping that everything will work**

is replaced by:

- setting up this repository (instructions are below; they are much less tedious
and error prone than manually setting up the individual components stated above.
Don't believe it? Read the Dockerfiles)
- deploying storm-alerts and **seeing that things are working** =)

## System Requirements

- **GNU** Make >= 3.8.2 (Required for .RECIPEPREFIX)
- Docker
- python 2.7.x
- virtualenv

## Setup for running storm-alerts within storm-docker

This section details the steps needed to setup the `storm-docker` repository
so it is ready for running the Storm topology in the
[storm-alerts](https://github.com/viki-org/storm-alerts) repository.

You should perform the following on the production server that you are going
to run [storm-alerts](https://github.com/viki-org/storm-alerts) on.

### On Storm's Logging Configuration

Storm 0.9.x makes use of [slf4j](http://www.slf4j.org/) as the abstract logger
and [logback](http://logback.qos.ch/) as the concrete logger.

**NOTE:** Whether storm-docker uses the `storm/cluster.xml` file as the actual
logging configuration file is just a guess, but one I'm relatively confident of
being correct.

When you build the Docker containers (steps are detailed below), the
`storm/cluster.xml` configuration file will be used as the `cluster.xml` file
for Storm. This happens to be the configuration file for logback, so you may
want to review it and change the logging configuration settings.

Additional documentation on logback can be found here:

- [http://logback.qos.ch/manual/index.html](http://logback.qos.ch/manual/index.html)
- [http://logback.qos.ch/documentation.html](http://logback.qos.ch/documentation.html)

### Python setup

We will be making use of [virtualenv](http://virtualenv.readthedocs.org/en/latest/)
for running the Storm Supervisor Docker. We also make use of the
[PyYAML](http://pyyaml.org/) library, and that requires some Python header
files.

On a Ubuntu-like system:

    sudo apt-get install python-virtualenv
    sudo apt-get install python-dev

### Install Docker

For Ubuntu Precise 12.04 (LTS), ensure that your Linux Kernel is a relatively
recent version (check the docs here:
http://docs.docker.io/installation/ubuntulinux/ for more information).

Use the following command from the top of the script at http://get.docker.io
to install Docker

    wget -qO- https://get.docker.io/ | bash

Verify your Docker installation:

    docker info

### Cloning this repository

Clone this repository, preferrably to `$HOME/workspace/storm-docker`.
At `$HOME/workspace`:

    git clone git@github.com:viki-org/storm-docker.git

The next few commands will be run from the `storm-docker` repository. Let us
go there:

    cd storm-docker

### Building the Docker images

Run the **GNU** `make` command (**NOTE:** Ensure that your version of GNU Make
is at least **3.8.2**, because we are using the `.RECIPEPREFIX` feature
available since that version). The default goal builds the Docker images:

    make

If this is the first time the Docker images are being built, this script will
take some time to complete.

### Configuring the Storm setup

**NOTE:** This step is **critical** to the correct functioning of the Storm
topology.

Copy the `storm-setup.yaml.sample` file in the `config` directory:

    cp config/storm-setup.yaml.sample config/storm-setup.yaml

And edit the `config/storm-setup.yaml` file. Documentation is available in
the `config/storm-setup.yaml.sample` file on how to fill up the file.

### Run the Docker containers

For a machine that is used to run **all** the following (in separate Docker
containers):

- Zookeeper
- Storm Nimbus
- Storm UI
- Storm Supervisor

Use the `start-storm.sh` script:

    ./start-storm.sh

For a machine which should run **some** of the above components (most notably, a
machine running only Storm Supervisor), refer to the same `start-storm.sh` file
and look at the individual commands in that script.

To provide a concrete example, the following command will run a
Storm Supervisor Docker container on **any** machine listed in the
`storm_supervisor_hosts` section of the `config/storm-setup.yaml` file:

    scripts/run-storm-supervisor.sh \
      --dns 127.0.0.1 --dns 8.8.8.8 --dns 8.8.8.4 \
      -p 49000:8000 -p 127.0.0.1:49022:22 \
      -p 6700:6700 -p 6701:6701 -p 6702:6702 -p 6703:6703 \
      --name supervisor \
      -d viki_data/storm-supervisor

Once you've run the desired Docker containers (minimally 1 Zookeeper,
1 Storm Nimbus, 1 Storm UI, 1 Storm Supervisor), you're ready to deploy a Storm
topology.

## To stop the Docker containers

Take a look inside the `destroy-storm.sh` script if you only need to stop
specific Docker containers. This can probably be done using `docker stop` (or
`docker kill`).

If you wish to stop everything (or if you're lazy), run the `destroy-storm.sh`
script:

    ./destroy-storm.sh

Do not be alarmed by the `docker rm` commands in the script. Rebuilding the
Docker images after a `docker rm` is faster than running the `rebuild.sh` script
for the first time as results are being cached.
