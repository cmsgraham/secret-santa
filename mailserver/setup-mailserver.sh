#!/bin/bash

# nameinahat.com Mail Server Setup Script
# Sets up secure mail server with DKIM, SPF, and proper configuration

set -e

echo "🔧 Setting up nameinahat.com Mail Server"
echo "========================================"

# Function to generate secure password hash
generate_password_hash() {
    local password="$1"
    # Use docker with a Python image that has crypt module
    docker run --rm python:3.9-alpine python -c "import crypt; print(crypt.crypt('$password', crypt.mksalt(crypt.METHOD_SHA512)))"
}

# Create data directories
echo "📁 Creating mail data directories..."
mkdir -p data/maildata data/mailstate ssl

# Generate DKIM keys
echo "🔐 Generating DKIM keys for nameinahat.com..."
if [ ! -f "config/opendkim/keys/nameinahat.com/mail.private" ]; then
    docker run --rm -v "$(pwd)/config/opendkim/keys/nameinahat.com":/keys \
        alpine/openssl genrsa -out /keys/mail.private 2048
    
    docker run --rm -v "$(pwd)/config/opendkim/keys/nameinahat.com":/keys \
        alpine/openssl rsa -in /keys/mail.private -pubout -out /keys/mail.public
    
    # Set proper permissions
    chmod 600 config/opendkim/keys/nameinahat.com/mail.private
    chmod 644 config/opendkim/keys/nameinahat.com/mail.public
    
    echo "✅ DKIM keys generated"
else
    echo "ℹ️  DKIM keys already exist"
fi

# Generate passwords for mail accounts
echo "🔑 Generating secure passwords for mail accounts..."

# Generate random passwords
SECRETSANTA_PASS=$(openssl rand -base64 16)
NOREPLY_PASS=$(openssl rand -base64 16)
ADMIN_PASS=$(openssl rand -base64 16)

# Create password hashes
SECRETSANTA_HASH=$(generate_password_hash "$SECRETSANTA_PASS")
NOREPLY_HASH=$(generate_password_hash "$NOREPLY_PASS")
ADMIN_HASH=$(generate_password_hash "$ADMIN_PASS")

# Update postfix-accounts.cf with real hashes
cat > config/postfix-accounts.cf << EOF
# Postfix accounts for nameinahat.com
secretsanta@nameinahat.com|$SECRETSANTA_HASH
noreply@nameinahat.com|$NOREPLY_HASH
admin@nameinahat.com|$ADMIN_HASH
EOF

echo "✅ Mail accounts configured"

# Save credentials securely
cat > .mail-credentials << EOF
# nameinahat.com Mail Server Credentials
# Keep this file secure and do not commit to git!

SECRETSANTA_EMAIL=secretsanta@nameinahat.com
SECRETSANTA_PASSWORD=$SECRETSANTA_PASS

NOREPLY_EMAIL=noreply@nameinahat.com
NOREPLY_PASSWORD=$NOREPLY_PASS

ADMIN_EMAIL=admin@nameinahat.com
ADMIN_PASSWORD=$ADMIN_PASS

# SMTP Settings for applications
SMTP_SERVER=172.233.171.101
SMTP_PORT=2587
SMTP_USER=secretsanta@nameinahat.com
SMTP_PASS=$SECRETSANTA_PASS
USE_TLS=true
EOF

chmod 600 .mail-credentials

echo ""
echo "🎉 Mail server setup complete!"
echo "=============================="
echo ""
echo "📧 Mail accounts created:"
echo "   • secretsanta@nameinahat.com"  
echo "   • noreply@nameinahat.com"
echo "   • admin@nameinahat.com"
echo ""
echo "🔐 Credentials saved in .mail-credentials (keep secure!)"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS records (see DNS_SETUP.md)"
echo "2. Start mail server: docker-compose up -d"
echo "3. Test mail delivery"
echo ""

# Display DKIM public key for DNS
echo "🔐 DKIM Public Key for DNS (TXT record):"
echo "Record Name: mail._domainkey.nameinahat.com"
echo "Record Value:"
echo "v=DKIM1; h=sha256; k=rsa; p=$(grep -v '^-' config/opendkim/keys/nameinahat.com/mail.public | tr -d '\n')"