# Forked from jplock/zookeeper (https://index.docker.io/u/jplock/zookeeper/)

FROM ubuntu
MAINTAINER viki-data data@viki.com

RUN echo "deb http://archive.ubuntu.com/ubuntu precise universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y unzip openjdk-6-jre-headless wget

RUN wget -q -O /opt/zookeeper-3.4.6.tar.gz http://apache.mirrors.pair.com/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
RUN tar -xzf /opt/zookeeper-3.4.6.tar.gz -C /opt
RUN cp /opt/zookeeper-3.4.6/conf/zoo_sample.cfg /opt/zookeeper-3.4.6/conf/zoo.cfg

ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64

EXPOSE 2181 2888 3888

ENTRYPOINT ["/opt/zookeeper-3.4.6/bin/zkServer.sh"]
CMD ["start-foreground"]
