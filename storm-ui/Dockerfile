FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

RUN /usr/bin/config-supervisord.sh ui

EXPOSE 8080

ENTRYPOINT ["/usr/bin/run-supervisord.py"]
