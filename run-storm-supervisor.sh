#!/bin/bash

if ! [ -d venv ]
then
  virtualenv venv
fi

. venv/bin/activate && \
  pip install -r requirements.txt && \
  python scripts/run-storm-supervisor.py &&
  deactivate
