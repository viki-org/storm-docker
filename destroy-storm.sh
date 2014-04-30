#!/bin/bash

docker stop ui; docker rm ui
docker stop supervisor; docker rm supervisor
docker stop nimbus; docker rm nimbus
docker stop zookeeper; docker rm zookeeper
