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

RUN mkdir /var/run/sshd
RUN apt-get install -y openssh-server
RUN echo 'root:root' | chpasswd
RUN sed -i 's/^\(PermitRootLogin\).*$/\1 yes/' /etc/ssh/sshd_config
RUN sed -i 's/^\(.*pam_loginuid\.so.*\)$/#\1/' /etc/pam.d/sshd

ADD ssh.supervisord.conf /etc/supervisor/conf.d/ssh.conf

EXPOSE 22

RUN /usr/bin/config-supervisord.sh supervisor
RUN /usr/bin/config-supervisord.sh logviewer

ENTRYPOINT ["/usr/bin/run-supervisord.py"]
