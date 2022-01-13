FROM httpd:latest

RUN apt-get update \
    && apt-get install -y vim locate

COPY index.html /usr/local/apache2/htdocs/index.html
COPY favicon.ico /usr/local/apache2/htdocs/favicon.ico
EXPOSE 80/tcp