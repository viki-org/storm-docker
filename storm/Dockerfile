FROM viki_data/base-storm-image
MAINTAINER viki-data data@viki.com

RUN mkdir /var/run/sshd
RUN apt-get install -y openssh-server
RUN echo 'root:root' | chpasswd

ADD ssh-supervisor /etc/supervisor/conf.d/ssh.conf
