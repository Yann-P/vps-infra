#!/bin/sh
printenv > /etc/environment
exec cron -f
