FROM ubuntu:14.04
MAINTAINER viki-data data@viki.com

RUN echo "deb http://archive.ubuntu.com/ubuntu precise universe" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.ccs.neu.edu/ubuntu precise universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y unzip openjdk-6-jdk wget supervisor python-dev python-pip
RUN pip install PyYAML==3.11

RUN wget -q -N http://mirrors.gigenet.com/apache/storm/apache-storm-0.9.2-incubating/apache-storm-0.9.2-incubating.zip
RUN unzip -o /apache-storm-0.9.2-incubating.zip -d /usr/share/
RUN rm /apache-storm-0.9.2-incubating.zip

ENV STORM_HOME /usr/share/apache-storm-0.9.2-incubating
RUN echo "STORM_HOME=/usr/share/apache-storm-0.9.2-incubating" | tee -a /etc/environment

RUN groupadd storm
RUN useradd --gid storm --home-dir /home/storm --create-home --shell /bin/bash storm
RUN chown -R storm:storm $STORM_HOME
RUN mkdir /var/log/storm
RUN chown -R storm:storm /var/log/storm
RUN ln -s $STORM_HOME/bin/storm /usr/bin/storm

# Add /mnt/storm directory (used for storing storm settings)
RUN mkdir -v /mnt/storm
RUN chown -R storm:storm /mnt/storm

ADD cluster.xml $STORM_HOME/logback/cluster.xml
ADD config-supervisord.sh /usr/bin/config-supervisord.sh
ADD run-supervisord.py /usr/bin/run-supervisord.py

ENV STORM_SETUP_YAML /storm-setup.yaml
ADD storm-setup.yaml $STORM_SETUP_YAML
RUN echo "STORM_SETUP_YAML=/storm-setup.yaml" | tee -a /etc/environment

RUN echo [supervisord] | tee -a /etc/supervisor/supervisord.conf
RUN echo nodaemon=true | tee -a /etc/supervisor/supervisord.conf
