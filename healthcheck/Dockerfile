FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    cron \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && echo "0 * * * * root python3 /healthcheck.py >> /tmp/cron_healthcheck.log 2>&1" > /etc/cron.d/healthcheck \
    && chmod 0644 /etc/cron.d/healthcheck

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
