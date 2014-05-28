FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

RUN /usr/bin/config-supervisord.sh nimbus 
RUN /usr/bin/config-supervisord.sh drpc

EXPOSE 6627
EXPOSE 3772
EXPOSE 3773

ENTRYPOINT ["/usr/bin/run-supervisord.py"]
