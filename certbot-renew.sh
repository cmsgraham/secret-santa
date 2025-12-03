#!/bin/bash
# Certbot certificate renewal script
# This should be run periodically (via cron or systemd timer)

set -e

echo "Starting certificate renewal..."

# Renew certificates
certbot renew \
    --webroot \
    --webroot-path /var/www/certbot \
    --quiet \
    --post-hook "nginx -s reload"

echo "Certificate renewal complete!"
