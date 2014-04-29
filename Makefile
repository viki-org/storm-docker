# Use '>' character instead of tab as the recipe prefix.
# This allows us to not use tabs in the Makefile
.RECIPEPREFIX = >

# Default build target
all: build-storm-docker-images

.PHONY: build-storm-docker-images build-base-storm-docker-image

build-storm-docker-images: build-base-storm-docker-image
> docker build -t="viki_data/storm" storm
> docker build -t="viki_data/storm-nimbus" storm-nimbus
> docker build -t="viki_data/storm-supervisor" storm-supervisor
> docker build -t="viki_data/storm-ui" storm-ui

build-base-storm-docker-image:
> docker build -t="viki_data/base-storm-image" base-storm-image
