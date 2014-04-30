storm-docker
============

This repository is forked from https://github.com/wurstmeister/storm-docker
and contains some edits that are specific to the
[storm-alerts](https://github.com/viki-org/storm-alerts) repository.

At Viki, we use this repository for setting up the
[storm-alerts](https://github.com/viki-org/storm-alerts) repository.
In fact, our Storm `alerts` topology runs within the docker containers built
from this repository.

## System Requirements

- **GNU** Make >= 3.8.2 (Required for .RECIPEPREFIX)
- Docker

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

### Install lxc

This is required if you wish to gain shell access to running Docker containers
(without resorting to running an SSH server or something similar within the
container), as outlined in
[this Stackoverflow answer](http://stackoverflow.com/questions/20932357/docker-enter-running-container-with-new-tty).

    sudo apt-get install lxc

### Install Docker

For Ubuntu Precise 12.04 (LTS), ensure that your Linux Kernel is a relatively
recent version (check the docs here:
http://docs.docker.io/installation/ubuntulinux/ for more information).

Use the following command from the top of the script at http://get.docker.io
to install Docker

    wget -qO- https://get.docker.io/ | sh

Check the information for your Docker installation:

    docker info

You should see something like this:

    Containers: 1

    Images: 4
    Storage Driver: aufs
     Root Dir: /var/lib/docker/aufs
     Dirs: 6
     Execution Driver: native-0.1
     Kernel Version: 3.11.0-19-generic
    WARNING: No swap limit support

**NOTE:** This step changing the Storage Driver to `btrfs` from `aufs` is not
strictly necessary. In fact, for our athena storm-alerts setup (which runs
fine), `aufs` is the Storage Driver.

If the value for `Storage Driver` is `aufs` we might want to change it to btrfs.
Edit the `/etc/default/docker` file and edit the `DOCKER_OPTS` line like so:

    DOCKER_OPTS="-s btrfs -e lxc"

The `-s btrfs` flag tells Docker to use btrfs as the storage driver.
The `-e lxc` flag tells Docker to use lxc as the execution driver (this allows
us to gain shell access to running Docker containers, as outlined in
[this Stackoverflow answer](http://stackoverflow.com/questions/20932357/docker-enter-running-container-with-new-tty)).

For these changes to take effect, restart the Docker server:

    service docker restart

Do a `docker info`, you should see something along the following:

    Containers: 0
    Images: 0
    Storage Driver: btrfs
    Execution Driver: native-0.1
    Kernel Version: 3.11.0-19-generic
    WARNING: No swap limit support

Notice that the storage driver is now `btrfs`. This is what we want.

### Cloning this repository

Clone this repository, preferrable to `$HOME/workspace/storm-docker`.
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

### Run the Docker containers

using the `start-storm.sh` script:

    ./start-storm.sh

And now the server is ready for running the
[storm-alerts](https://github.com/viki-org/storm-alerts) repository. Follow the
instructions [here](https://github.com/viki-org/storm-alerts) for setting up the
storm-alerts repository if you intend to deploy the storm-alerts topology to the
server you just did the above setup on.

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

## FAQ - Debugging stuff to do with Docker containers

**NOTE:** This section is written from my memory (which tends to be vague) so it
may not be as accurate as the sections above. In fact, you should correct the
information here should you discover any mistakes.

#### Qn: storm-alerts has been running for some time but for some reason it went down. I do not see the storm-docker containers when I run `docker ps` . What's wrong?

**Answer:** Most likely your Docker containers were killed using `docker stop`
or `docker kill` (and perhaps followed by `docker rm`).
Do a `docker ps -a` and check if the containers are around. If the containers
are around, then they were most likely killed by `docker stop` or `docker kill`.
If you do not see the containers from the output of `docker ps -a`, most
probably they were removed using `docker rm`.

In any case, the simplest solution is to execute the `destroy-storm.sh` script
in this repository, followed by the `make` command to rebuild the Docker images,
then the `start-storm.sh` script (this might not work).
