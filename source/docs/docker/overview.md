---
title: Dockerfile Organization
---

Dockerfile Organization
=======================

There are a few Dockerfiles in this repository, placed in the following folders,
whose names should be self explanatory:

- zookeeper
- base-storm
- storm-nimbus
- storm-ui
- storm-supervisor

`base-storm` is an "abstract" Dockerfile and is not actually run.
It is used as a foundation for the `storm-nimbus`, `storm-ui` and
`storm-supervisor` Dockerfiles. 

We shall go over each of the Dockerfiles in more detail in the other pages of
this section.
