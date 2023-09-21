FROM nginx:latest
RUN rm /etc/nginx/nginx.conf
STOPSIGNAL SIGKILL
COPY nginx.conf /etc/nginx/nginx.conf