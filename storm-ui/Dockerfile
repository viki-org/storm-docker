FROM viki_data/base-storm-image
MAINTAINER viki-data data@viki.com

RUN /usr/bin/config-supervisord.sh ui

EXPOSE 8080
CMD /usr/bin/start-supervisor.sh
