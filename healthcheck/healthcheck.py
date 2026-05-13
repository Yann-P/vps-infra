#!/usr/bin/env python3

import os
import smtplib
import subprocess
from datetime import datetime, timezone
from email.message import EmailMessage

import tomllib

ALERT_EMAIL = os.environ["ALERT_EMAIL"]
MAIL_FROM = os.environ["MAIL_FROM"]
SMTP_HOST = os.environ.get("SMTP_HOST", "host.docker.internal")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))

with open("/config.toml", "rb") as f:
    config = tomllib.load(f)

thresholds = config["thresholds"]
checks = config["checks"]

failures = []
details = []

loadavg = os.getloadavg()[0]
if loadavg > thresholds["max_load_avg"]:
    failures.append(f"loadavg({loadavg})")
    result = subprocess.run(
        ["ps", "aux", "--sort=-%cpu"], capture_output=True, text=True
    )
    details.append("Top processes:\n" + "\n".join(result.stdout.splitlines()[:6]))

for url in checks["http"]:
    result = subprocess.run(
        ["curl", "-o", "/dev/null", "-s", "-w", "%{http_code}", url],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip() != "200":
        failures.append(f"{url}({result.stdout.strip()})")

result = subprocess.run(["df", "-k"], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if thresholds["disk_device"] in line:
        available_kb = int(line.split()[3])
        if available_kb < thresholds["min_disk_kb"]:
            failures.append("storage")
            df_h = subprocess.run(["df", "-h"], capture_output=True, text=True)
            details.append("Disk usage:\n" + df_h.stdout)
        break

borgmatic_status = "/borgmatic-status/last-success"
if os.path.exists(borgmatic_status):
    with open(borgmatic_status) as f:
        last_success = datetime.fromtimestamp(int(f.read().strip()), tz=timezone.utc)
    age_h = (datetime.now(tz=timezone.utc) - last_success).total_seconds() / 3600
    if age_h > thresholds["borgmatic_max_age_h"]:
        failures.append(f"Borgmatic({age_h:.1f}h ago)")
else:
    failures.append("Borgmatic(no-status-file)")

if failures:
    subject = "Server Monitoring: " + " ".join(failures)
    body = "\n\n".join(details) if details else ""

    print("FAILURES:", subject)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = ALERT_EMAIL
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)
