FROM ghcr.io/borgmatic-collective/borgmatic:latest
RUN apk add --no-cache postgresql15-client
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
