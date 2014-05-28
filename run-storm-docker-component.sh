#!/bin/bash

if ! [ -d venv ]
then
  virtualenv venv
fi

. venv/bin/activate && \
  pip install -r requirements.txt && \
  python -m docker_python_helpers.docker_run \
    docker_python_helpers/docker_run.py $@ && \
  deactivate
