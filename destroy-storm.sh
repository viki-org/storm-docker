#!/bin/bash

docker stop zookeeper; docker rm zookeeper
docker stop nimbus; docker rm nimbus
docker stop supervisor; docker rm supervisor
docker stop ui; docker rm ui
