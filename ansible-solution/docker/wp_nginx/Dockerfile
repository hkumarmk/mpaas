FROM nginx:stable
ENV WEB_PORT=80
ENV SERVER_NAME=localhost
ENV BACKEND_SERVER=localhost
ENV BACKEND_PORT=9000
COPY entrypoint.sh /
VOLUME ["/var/www/html", "/var/log/nginx"]
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh
