# Default build target
all: build-storm-docker-containers

.PHONY: check-storm-setup-yaml-exists build-storm-docker-containers \
  build-base-storm-docker-container build-zookeeper-docker-container \
  check-config-cluster-xml-exists check-config-zoo-cfg-exists

STORM_SETUP_YAML := storm-setup.yaml
CONFIG_STORM_SETUP_YAML := $(addprefix config/,$(STORM_SETUP_YAML))
CONFIG_STORM_SETUP_YAML_SAMPLE := \
  $(addsuffix .sample,$(CONFIG_STORM_SETUP_YAML))
DOCKER_STORM_SETUP_YAML := $(addprefix base-storm/,$(STORM_SETUP_YAML))
ZK_STORM_SETUP_YAML := $(addprefix zookeeper/,$(STORM_SETUP_YAML))

check-storm-setup-yaml-exists:
	test -f $(CONFIG_STORM_SETUP_YAML) || \
      { echo \"$(CONFIG_STORM_SETUP_YAML)\" does not exist. Please create it from \
      \"$(CONFIG_STORM_SETUP_YAML_SAMPLE)\" and try again. Exiting.; exit 1; }

CLUSTER_XML := cluster.xml
CONFIG_CLUSTER_XML := $(addprefix config/,$(CLUSTER_XML))
CONFIG_CLUSTER_XML_SAMPLE := $(addsuffix .sample,$(CONFIG_CLUSTER_XML))
BASE_STORM_CLUSTER_XML := $(addprefix base-storm/,$(CLUSTER_XML))

check-config-cluster-xml-exists:
	test -f $(CONFIG_CLUSTER_XML) || \
      { echo \"$(CONFIG_CLUSTER_XML)\" does not exist. Please create it from \
      \"$(CONFIG_CLUSTER_XML_SAMPLE)\" and try again. Exiting.; exit 1; }

# For `zoo.cfg`
ZOO_CFG := zoo.cfg
CONFIG_ZOO_CFG := $(addprefix config/,$(ZOO_CFG))
CONFIG_ZOO_CFG_SAMPLE := $(addsuffix .sample,$(CONFIG_ZOO_CFG))
ZOOKEEPER_ZOO_CFG := $(addprefix zookeeper/,$(ZOO_CFG))

check-config-zoo-cfg-exists:
	test -f $(CONFIG_ZOO_CFG) || \
      { echo \"$(CONFIG_ZOO_CFG)\" does not exist. Please create it from \
      \"$(CONFIG_ZOO_CFG_SAMPLE)\" and try again. Exiting.; exit 1; }

build-storm-docker-containers: check-storm-setup-yaml-exists \
  check-config-cluster-xml-exists build-base-storm-docker-container \
  build-zookeeper-docker-container
	docker build -t="viki_data/storm-nimbus" storm-nimbus
	docker build -t="viki_data/storm-supervisor" storm-supervisor
	docker build -t="viki_data/storm-ui" storm-ui

# Get md5 checksums of source and destination `storm-setup.yaml`
STORM_SETUP_YAML_SOURCE_CHECKSUM = $(shell \
  md5sum < $(CONFIG_STORM_SETUP_YAML) | awk '{print $$1}' || echo "source" \
)
STORM_SETUP_YAML_DEST_CHECKSUM = $(shell \
  md5sum < $(DOCKER_STORM_SETUP_YAML) | awk '{print $$1}' || echo "dest" \
)

# Get MD5 checksums of source and destination `cluster.xml`
BASE_STORM_CLUSTER_XML_SOURCE_CHECKSUM = $(shell \
  md5sum < $(CONFIG_CLUSTER_XML) | awk '{print $$1}' || echo "source" \
)
BASE_STORM_CLUSTER_XML_DEST_CHECKSUM = $(shell \
  md5sum < $(BASE_STORM_CLUSTER_XML) | awk '{print $$1}' || echo "dest" \
)

build-base-storm-docker-container: check-config-cluster-xml-exists
ifneq ($(STORM_SETUP_YAML_SOURCE_CHECKSUM),$(STORM_SETUP_YAML_DEST_CHECKSUM))
# Only copy `config/storm-setup.yaml` to `base-storm/storm-setup.yaml` if their
# contents differ.
# If the copy operation is executed everytime, the `docker build` step will not
# make use of the cache after the step where `base-storm/storm-setup.yaml` is
# added into the Docker container.
	cp $(CONFIG_STORM_SETUP_YAML) $(DOCKER_STORM_SETUP_YAML)
endif
ifneq ($(BASE_STORM_CLUSTER_XML_SOURCE_CHECKSUM),$(BASE_STORM_CLUSTER_XML_DEST_CHECKSUM))
# Copy the `config/cluster.xml` file to `base-storm/cluster.xml` if their
# contents differ (or if `base-storm/cluster.xml` does not exist)
	cp $(CONFIG_CLUSTER_XML) $(BASE_STORM_CLUSTER_XML)
endif
	docker build -t="viki_data/base-storm" base-storm

STORM_SETUP_YAML_ZK_CHECKSUM = $(shell \
  md5sum < $(ZK_STORM_SETUP_YAML) | awk '{print $$1}' || echo "dest" \
)

# MD5 checksum for `config/zoo.cfg`
ZOOKEEPER_ZOO_CFG_SOURCE_CHECKSUM = $(shell \
  md5sum < $(CONFIG_ZOO_CFG) | awk '{print $$1}' || echo "source" \
)
# MD5 checksum for `zookeeper/zoo.cfg`
ZOOKEEPER_ZOO_CFG_DEST_CHECKSUM = $(shell \
  md5sum < $(ZOOKEEPER_ZOO_CFG) | awk '{print $$1}' || echo "dest" \
)

build-zookeeper-docker-container: check-storm-setup-yaml-exists \
  check-config-zoo-cfg-exists
ifneq ($(STORM_SETUP_YAML_SOURCE_CHECKSUM),$(STORM_SETUP_YAML_ZK_CHECKSUM))
# Same usage as `build-base-storm-docker-container` rule
	cp $(CONFIG_STORM_SETUP_YAML) $(ZK_STORM_SETUP_YAML)
endif
ifneq ($(ZOOKEEPER_ZOO_CFG_SOURCE_CHECKSUM),$(ZOOKEEPER_ZOO_CFG_DEST_CHECKSUM))
	cp $(CONFIG_ZOO_CFG) $(ZOOKEEPER_ZOO_CFG)
endif
	docker build -t="viki_data/zookeeper" zookeeper

# vim: set ts=4:sts=4:sw=4:noet #
