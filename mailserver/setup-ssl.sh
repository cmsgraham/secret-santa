#!/bin/bash

# SSL Certificate Setup for nameinahat.com Mail Server
# This script helps set up SSL certificates for secure mail operation

set -e

echo "🔒 SSL Certificate Setup for nameinahat.com"
echo "==========================================="

# Create SSL directory
mkdir -p ssl

echo "📋 SSL Certificate Options:"
echo "1. Self-signed certificate (for testing)"
echo "2. Let's Encrypt certificate (recommended for production)"
echo "3. Use existing certificate files"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🔧 Creating self-signed certificate..."
        
        # Generate self-signed certificate
        openssl req -new -x509 -days 365 -nodes \
            -out ssl/fullchain.pem \
            -keyout ssl/privkey.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=mail.nameinahat.com/emailAddress=admin@nameinahat.com"
        
        echo "✅ Self-signed certificate created"
        echo "⚠️  Warning: Self-signed certificates will show security warnings"
        ;;
        
    2)
        echo "🔧 Setting up Let's Encrypt certificate..."
        
        # Check if certbot is installed
        if ! command -v certbot &> /dev/null; then
            echo "❌ Certbot not found. Installing..."
            
            # Install certbot based on OS
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                sudo apt update && sudo apt install -y certbot
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                brew install certbot
            else
                echo "❌ Unsupported OS. Please install certbot manually."
                exit 1
            fi
        fi
        
        echo "🌐 Obtaining Let's Encrypt certificate for mail.nameinahat.com..."
        echo "⚠️  Make sure DNS A record for mail.nameinahat.com points to this server!"
        
        read -p "Continue with Let's Encrypt? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            # Use standalone mode (requires port 80 to be available)
            sudo certbot certonly --standalone \
                --preferred-challenges http \
                -d mail.nameinahat.com \
                --email admin@nameinahat.com \
                --agree-tos \
                --no-eff-email
            
            # Copy certificates to our ssl directory
            sudo cp /etc/letsencrypt/live/mail.nameinahat.com/fullchain.pem ssl/
            sudo cp /etc/letsencrypt/live/mail.nameinahat.com/privkey.pem ssl/
            sudo chown $(whoami):$(whoami) ssl/*.pem
            
            echo "✅ Let's Encrypt certificate installed"
            
            # Set up auto-renewal
            echo "🔄 Setting up certificate auto-renewal..."
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nameinahat-mail") | crontab -
            
        else
            echo "❌ Let's Encrypt setup cancelled"
        fi
        ;;
        
    3)
        echo "📁 Using existing certificate files..."
        echo "Place your certificate files in the ssl/ directory:"
        echo "  - ssl/fullchain.pem (full certificate chain)"
        echo "  - ssl/privkey.pem (private key)"
        echo ""
        
        if [[ -f "ssl/fullchain.pem" && -f "ssl/privkey.pem" ]]; then
            echo "✅ Certificate files found"
        else
            echo "❌ Certificate files not found in ssl/ directory"
            echo "Please place your certificate files and run this script again"
            exit 1
        fi
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Verify certificate files exist and are valid
if [[ -f "ssl/fullchain.pem" && -f "ssl/privkey.pem" ]]; then
    echo ""
    echo "🔍 Verifying certificate..."
    
    # Check certificate validity
    cert_info=$(openssl x509 -in ssl/fullchain.pem -text -noout)
    
    if echo "$cert_info" | grep -q "mail.nameinahat.com"; then
        echo "✅ Certificate is valid for mail.nameinahat.com"
        
        # Show certificate expiration
        exp_date=$(openssl x509 -in ssl/fullchain.pem -noout -dates | grep notAfter | cut -d= -f2)
        echo "📅 Certificate expires: $exp_date"
        
    else
        echo "⚠️  Certificate does not contain mail.nameinahat.com"
        echo "This may cause SSL/TLS errors"
    fi
    
    # Set proper permissions
    chmod 644 ssl/fullchain.pem
    chmod 600 ssl/privkey.pem
    
    echo ""
    echo "🎉 SSL certificate setup complete!"
    echo "Mail server is ready for secure connections"
    
else
    echo "❌ SSL certificate setup failed"
    echo "Certificate files not found in ssl/ directory"
    exit 1
fi