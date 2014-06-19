---
title: storm-supervisor Docker
---

storm-supervisor Docker
=======================

Dockerfile: `storm-supervisor/Dockerfile`

Entrypoint source file: `base-storm/run-supervisord.py`

## Services running in this Docker

- dnsmasq
- SSH daemon (accessible only from the machine running this Docker)
- Storm Supervisor
- Storm Logviewer

### dnsmasq

Remember in `config/storm-setup.yaml`, you filled up aliases for the entries
under the **storm.supervisor.hosts** key? Storm Supervisor uses those aliases
to identify other Storm Supervisor in the Storm cluster, and upon receiving
a DNS lookup request for an alias in that section, dnsmasq returns the
IP address for it. Use of dnsmasq is required due to `/etc/hosts` being a
read-only file in Docker; for the storm-supervisor Docker container, dnsmasq
essentially serves the same purpose as `/etc/hosts` conventionally does.

Opening the `start-storm.sh` script, we see the `--dns 127.0.0.1`,
`--dns 8.8.8.8` and `--dns 8.8.4.4` arguments. These are eventually passed to
the `docker run` command. The `--dns 127.0.0.1` tells the running Docker
container to use dnsmasq for DNS resolution, followed by the
[Google DNS servers](https://developers.google.com/speed/public-dns/).

### SSH daemon

The SSH daemon runs at port 22 of the Docker container, but is mapped to
port 49022 of the host.

To access a running `storm-supervisor` Docker from its host machine:

    ssh -p 49022 root@localhost

## On the Entrypoint

The `storm-supervisor` Docker's entrypoint is the
`base-storm/run-supervisord.py` Python script.

For the `storm-supervisor` Docker container, the entrypoint script creates an
additional hosts file that dnsmasq picks up.
This hosts file contains the aliases for **all** Storm Supervisor nodes and the
IP addresses for those aliases (the details are provided by the user in the
`config/storm-setup.yaml` file) so that it can perform DNS resolutions for those
aliases. This is necessary due to Storm Supervisor using aliases to identify
other Storm Supervisor nodes.
