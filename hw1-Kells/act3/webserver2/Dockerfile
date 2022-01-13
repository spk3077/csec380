FROM httpd:latest
# Install vim for testing
RUN apt-get update \
    && apt-get install -y vim
    
COPY index.html /usr/local/apache2/htdocs/index.html
COPY favicon.ico /usr/local/apache2/htdocs/favicon.ico
EXPOSE 80/tcp