#!/bin/sh
set -e

borgmatic init --remote-path=borg-1.4

echo "[borgmatic] Writing crontab"

# 2 AM
echo "0 2 * * * borgmatic --verbosity 1 2>&1 | tee -a /var/log/borgmatic.log" > /etc/crontabs/root

echo "[borgmatic] Starting cron daemon..."

exec crond -f -l 8
