# Use '>' character instead of tab as the recipe prefix.
# This allows us to not use tabs in the Makefile
.RECIPEPREFIX = >

# Default build target
all: build-storm-docker-containers

.PHONY: check-storm-setup-yaml-exists build-storm-docker-containers \
  build-base-storm-docker-container build-zookeeper-docker-container

STORM_SETUP_YAML := storm-setup.yaml
CONFIG_STORM_SETUP_YAML := $(addprefix config/,$(STORM_SETUP_YAML))
CONFIG_STORM_SETUP_YAML_SAMPLE := \
  $(addsuffix .sample,$(CONFIG_STORM_SETUP_YAML))
DOCKER_STORM_SETUP_YAML := $(addprefix base-storm/,$(STORM_SETUP_YAML))
ZK_STORM_SETUP_YAML := $(addprefix zookeeper/,$(STORM_SETUP_YAML))

check-storm-setup-yaml-exists:
> test -f $(CONFIG_STORM_SETUP_YAML) || \
  { echo \"$(CONFIG_STORM_SETUP_YAML)\" does not exist. Please create it from \
    \"$(CONFIG_STORM_SETUP_YAML_SAMPLE)\" and try again. Exiting.; exit 1; }

build-storm-docker-containers: check-storm-setup-yaml-exists \
    build-base-storm-docker-container build-zookeeper-docker-container
> docker build -t="viki_data/storm-nimbus" storm-nimbus
> docker build -t="viki_data/storm-supervisor" storm-supervisor
> docker build -t="viki_data/storm-ui" storm-ui

# Get md5 checksums of source and destination `storm-setup.yaml`
STORM_SETUP_YAML_SOURCE_CHECKSUM = $(shell \
  md5sum < $(CONFIG_STORM_SETUP_YAML) | awk '{print $$1}' || echo "source" \
)
STORM_SETUP_YAML_DEST_CHECKSUM = $(shell \
  md5sum < $(DOCKER_STORM_SETUP_YAML) | awk '{print $$1}' || echo "dest" \
)

build-base-storm-docker-container:
ifneq ($(STORM_SETUP_YAML_SOURCE_CHECKSUM),$(STORM_SETUP_YAML_DEST_CHECKSUM))
# Only copy `config/storm-setup.yaml` to `base-storm/storm-setup.yaml` if their
# contents differ.
# If the copy operation is executed everytime, the `docker build` step will not
# make use of the cache after the step where `base-storm/storm-setup.yaml` is
# added into the Docker container.
> cp $(CONFIG_STORM_SETUP_YAML) $(DOCKER_STORM_SETUP_YAML)
endif
> docker build -t="viki_data/base-storm" base-storm

STORM_SETUP_YAML_ZK_CHECKSUM = $(shell \
  md5sum < $(ZK_STORM_SETUP_YAML) | awk '{print $$1}' || echo "dest" \
)

build-zookeeper-docker-container: check-storm-setup-yaml-exists
ifneq ($(STORM_SETUP_YAML_SOURCE_CHECKSUM),$(STORM_SETUP_YAML_ZK_CHECKSUM))
# Same usage as `build-base-storm-docker-container` rule
> cp $(CONFIG_STORM_SETUP_YAML) $(ZK_STORM_SETUP_YAML)
endif
> docker build -t="viki_data/zookeeper" zookeeper
