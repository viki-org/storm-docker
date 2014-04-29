# Use '>' character instead of tab as the recipe prefix.
# This allows us to not use tabs in the Makefile
.RECIPEPREFIX = >

# Default build target
all: build-storm-docker-containers

.PHONY: build-storm-docker-containers build-base-storm-docker-container

build-storm-docker-containers: build-base-storm-docker-container
> docker build -t="viki_data/storm-nimbus" storm-nimbus
> docker build -t="viki_data/storm-supervisor" storm-supervisor
> docker build -t="viki_data/storm-ui" storm-ui

build-base-storm-docker-container:
> docker build -t="viki_data/base-storm" base-storm
