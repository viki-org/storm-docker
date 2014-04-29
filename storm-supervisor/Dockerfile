FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

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
CMD /usr/bin/start-supervisor.sh
