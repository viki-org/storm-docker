FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

# Install dnsmasq for resolving hostnames for other storm-supervisor
RUN apt-get install -y dnsmasq
# Add configuration for dnsmasq
RUN echo 'user=root' | tee -a /etc/dnsmasq.conf
RUN echo 'domain-needed' | tee -a /etc/dnsmasq.conf
RUN echo 'bogus-priv' | tee -a /etc/dnsmasq.conf
RUN echo 'addn-hosts=/etc/dnsmasq-extra-hosts' | tee -a /etc/dnsmasq.conf
# Add supervisord config for dnsmasq
ADD dnsmasq.supervisord.conf /etc/supervisor/conf.d/dnsmasq.conf
# Add Python script for setting up $STORM_HOME/conf/storm.yaml
ADD setup-and-run-storm-supervisor.py /usr/bin/setup-and-run-storm-supervisor.py

RUN mkdir /var/run/sshd
RUN apt-get install -y openssh-server
RUN echo 'root:root' | chpasswd

ADD ssh-supervisor /etc/supervisor/conf.d/ssh.conf

EXPOSE 6700
EXPOSE 6701
EXPOSE 6702
EXPOSE 6703
EXPOSE 8000
EXPOSE 22

RUN /usr/bin/config-supervisord.sh supervisor
RUN /usr/bin/config-supervisord.sh logviewer
ENTRYPOINT ["/usr/bin/setup-and-run-storm-supervisor.py"]
