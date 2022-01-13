FROM varnish:latest
RUN apt-get update \
    && apt-get install -y net-tools
COPY default.vcl /etc/varnish/default.vcl
EXPOSE 80/tcp