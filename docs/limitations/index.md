---
title: Limitations
---

storm-docker Limitations
========================

storm-docker is by no means a perfect piece of software.
As stated in the README, it is meant as a starting point for distributed,
multiple server setups.
In fact, you are highly encouraged to dig into the source code and hack on it
until it suits your use case.

Recently, there's an article written by [Matt Jaynes](https://devopsu.com/)
that addresses misconceptions about Docker and some mistakes that beginners
make when writing Dockerfiles for their applications.

- Link to the article: [https://devopsu.com/blog/docker-misconceptions/](https://devopsu.com/blog/docker-misconceptions/)
- Hacker News discussion: [https://news.ycombinator.com/item?id=7869904](https://news.ycombinator.com/item?id=7869904)

After reading Matt Jaynes' article, I can't help but feel that I've overlooked
many things he mentioned in the
**Misconception: If I learn Docker then I don't have to learn the other systems
stuff!** section.

Not long after I happened to chance across this:

- [http://phusion.github.io/baseimage-docker/](http://phusion.github.io/baseimage-docker/)
- [Github repository for the above](https://github.com/phusion/baseimage-docker)

and it confirmed my suspicions.

So I shall highlight some major limitations of storm-docker here.

## Managing Logging

This is probably the most serious issue not addressed by storm-docker.
While there are log files for various Storm components and Zookeeper, they will
be gone once their Docker container is stopped.

## Non persistent storage

Similar in spirit to the **Managing Logging** section. There may be other files
that we want to preserve on more persistent storage, but this is currently not
being taken care of.

## Configuration Management

For storm-docker, all configuration is done within the Dockerfiles.
There is no provisioning tool used to manage configuration of the various
Docker containers.
