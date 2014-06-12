#!/bin/bash

# Copies the sample configuration files to the `config` folder but without
# the `.sample` extension.
#
# This DOES NOT overwrite any existing destination files

cp -n config/cluster.xml{.sample,}
cp -n config/storm-setup.yaml{.sample,}
cp -n config/zoo.cfg{.sample,}
