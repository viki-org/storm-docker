FROM viki_data/base-storm
MAINTAINER viki-data data@viki.com

RUN /usr/bin/config-supervisord.sh ui

ENTRYPOINT ["/usr/bin/run-supervisord.py"]
