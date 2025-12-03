#!/bin/bash
# Certbot initialization script for Let's Encrypt certificate generation

set -e

DOMAIN="nameinahat.com"
EMAIL="your-email@example.com"  # Change this to your email
CERTBOT_DIR="/etc/letsencrypt"
CHALLENGE_DIR="/var/www/certbot"

echo "Starting Certbot certificate initialization..."

# Create challenge directory if it doesn't exist
mkdir -p "$CHALLENGE_DIR"

# Check if certificate already exists
if [ -d "$CERTBOT_DIR/live/$DOMAIN" ]; then
    echo "Certificate already exists for $DOMAIN"
    echo "To renew, run: certbot renew"
    exit 0
fi

# Check if we're in staging or production mode
if [ "$1" = "staging" ]; then
    echo "Using Let's Encrypt STAGING environment (for testing)"
    STAGING_FLAG="--staging"
else
    echo "Using Let's Encrypt PRODUCTION environment"
    STAGING_FLAG=""
fi

# Create self-signed cert temporarily (so Nginx can start)
echo "Creating temporary self-signed certificate..."
openssl req -x509 -newkey rsa:4096 -keyout /tmp/privkey.pem -out /tmp/fullchain.pem \
    -days 1 -nodes -subj "/CN=$DOMAIN" 2>/dev/null || true

mkdir -p "$CERTBOT_DIR/live/$DOMAIN"
cp /tmp/privkey.pem "$CERTBOT_DIR/live/$DOMAIN/privkey.pem" 2>/dev/null || true
cp /tmp/fullchain.pem "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" 2>/dev/null || true

# Request certificate from Let's Encrypt
echo "Requesting certificate from Let's Encrypt..."
certbot certonly \
    --webroot \
    --webroot-path="$CHALLENGE_DIR" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    $STAGING_FLAG

echo "Certificate initialization complete!"
echo "Nginx can now be started."
