# Forked from jplock/zookeeper (https://index.docker.io/u/jplock/zookeeper/)

FROM ubuntu
MAINTAINER viki-data data@viki.com

RUN echo "deb http://archive.ubuntu.com/ubuntu precise universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y unzip openjdk-6-jre-headless wget supervisor

RUN wget -q -O /opt/zookeeper-3.4.6.tar.gz http://apache.mirrors.pair.com/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
RUN tar -xzf /opt/zookeeper-3.4.6.tar.gz -C /opt
RUN rm /opt/zookeeper-3.4.6.tar.gz
# Create Zookeeper snapshot directory (dataDir)
RUN mkdir -p /var/lib/zookeeper
# Create Zookeeper transaction log directory (dataLogDir)
RUN mkdir /zookeeper-transactions
# Add custom Zookeeper configuration file
ADD zoo.cfg /opt/zookeeper-3.4.6/conf/zoo.cfg
# Disable Zookeeper `dataDir` autocreation, read:
#     http://zookeeper.apache.org/doc/trunk/zookeeperAdmin.html#Disabling+data+directory+autocreation
ENV ZOO_DATADIR_AUTOCREATE_DISABLE 1

# Logs folder for supervisord
RUN mkdir -p /var/log/supervisor

# Append supervisord global settings to /etc/supervisor/supervisord.conf
RUN echo [supervisord] | tee -a /etc/supervisor/supervisord.conf
RUN echo nodaemon=true | tee -a /etc/supervisor/supervisord.conf

# Add supervisor configuration file for zookeeper
ADD supervisord.conf /etc/supervisor/conf.d/zookeeper.conf

ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64

EXPOSE 2181 2888 3888

ENTRYPOINT ["supervisord"]
