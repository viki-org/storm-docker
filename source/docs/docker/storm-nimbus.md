---
title: storm-nimbus
---

storm-nimbus Docker
===================

Dockerfile: `storm-nimbus/Dockerfile`

Entrypoint source file: `base-storm/run-supervisord.py`

## Services running in this Docker

- Storm Nimbus
- Storm DRPC

## Additional Information

Nimbus happens to be Storm's single point of failure (SPOF), kind of.
See this article:
[chttp://storm.incubator.apache.org/documentation/Fault-tolerance.html](http://storm.incubator.apache.org/documentation/Fault-tolerance.html)
for more information on what happens if Storm Nimbus fails.

storm-docker follows the advice stated in the above link, and uses
[supervisord](http://supervisord.org/) to launch Storm Nimbus.
