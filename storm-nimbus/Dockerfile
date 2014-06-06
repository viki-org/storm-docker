FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

RUN /usr/bin/config-supervisord.sh nimbus 
RUN /usr/bin/config-supervisord.sh drpc

ENTRYPOINT ["/usr/bin/run-supervisord.py"]
