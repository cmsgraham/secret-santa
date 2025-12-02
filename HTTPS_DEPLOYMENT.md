# HTTPS Deployment Guide for 172.233.185.208

## Prerequisites
- New server at 172.233.185.208 is ready with Docker installed
- Repository is cloned at `/opt/secret-santa`
- DNS for `nameinahat.com` is pointing to `172.233.185.208`

## Step-by-Step Deployment

### 1. Configure Environment Variables

Create `.env` file:
```bash
cd /opt/secret-santa
cp .env.example .env
# Edit .env with proper values:
nano .env
```

**Important variables to set:**
```bash
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://secret_santa:password@db:5432/secret_santa_db
DEBUG=false
FLASK_ENV=production

# SMTP settings (same as before)
SMTP_SERVER=172.233.171.101
SMTP_PORT=2587
SMTP_USERNAME=secretsanta@nameinahat.com
SMTP_PASSWORD=xiWbEMsDXggUKUXqYSwFIg==
SMTP_FROM_EMAIL=secretsanta@nameinahat.com
SMTP_FROM_NAME=Secret Santa
SMTP_USE_TLS=true

# HTTPS/Proxy settings
APP_URL=https://nameinahat.com
TRUST_PROXY=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### 2. Initialize Certbot Certificate (Staging First!)

Before starting the full stack, initialize certificates:

```bash
# Build Certbot container
docker build -f Dockerfile.certbot -t secret-santa-certbot .

# Run initialization in STAGING mode (for testing)
docker run -it --rm \
  -v /opt/secret-santa/certbot_certs:/etc/letsencrypt \
  -v /opt/secret-santa/certbot_www:/var/www/certbot \
  secret-santa-certbot \
  /usr/local/bin/init-certbot.sh staging

# IMPORTANT: Check for errors. If successful, proceed to production
```

**Output should show:**
```
Starting Certbot certificate initialization...
Using Let's Encrypt STAGING environment (for testing)
Creating temporary self-signed certificate...
Requesting certificate from Let's Encrypt...
Certificate initialization complete!
```

### 3. Generate Production Certificates

Once staging works, initialize production:

```bash
docker run -it --rm \
  -v /opt/secret-santa/certbot_certs:/etc/letsencrypt \
  -v /opt/secret-santa/certbot_www:/var/www/certbot \
  secret-santa-certbot \
  /usr/local/bin/init-certbot.sh production
```

### 4. Start Docker Containers

```bash
cd /opt/secret-santa
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Expected output:**
```
NAME                           COMMAND                  SERVICE      STATUS
secret-santa-app-1             "python app_v2.py"       app          Up (healthy)
secret-santa-db-1              "docker-entrypoint..."   db           Up (healthy)
secret-santa-redis-1           "redis-server"           redis        Up (healthy)
secret-santa-nginx-1           "nginx -g daemon off"    nginx        Up (healthy)
secret-santa-certbot-1         "crond -f"               certbot      Up
```

### 5. Verify HTTPS Works

```bash
# From your local machine:
curl -I https://nameinahat.com

# Should return:
# HTTP/2 200
# strict-transport-security: max-age=31536000; includeSubDomains; preload
# x-frame-options: SAMEORIGIN
# x-content-type-options: nosniff
```

### 6. Test HTTP→HTTPS Redirect

```bash
curl -I http://172.233.185.208/

# Should redirect to HTTPS:
# HTTP/1.1 301 Moved Permanently
# Location: https://172.233.185.208/
```

### 7. Check Certificate Details

```bash
# On server:
docker-compose exec nginx openssl x509 -in /etc/letsencrypt/live/nameinahat.com/fullchain.pem -text -noout

# Should show valid certificate for nameinahat.com
```

### 8. Test Certificate Renewal

```bash
# Manually trigger renewal (certbot should renew at 3 AM daily)
docker-compose exec certbot /usr/local/bin/certbot-renew.sh

# Check logs
docker-compose logs certbot
```

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f app
docker-compose logs -f certbot
```

### Check Container Health
```bash
docker-compose ps

# Detailed status
docker health inspect secret-santa-app-1
docker health inspect secret-santa-nginx-1
```

### Certificate Status
```bash
docker-compose exec certbot certbot certificates

# Should show valid certificate with renewal date
```

## Troubleshooting

### Certificate Not Found Error
```
error connecting to /etc/letsencrypt/live/nameinahat.com/fullchain.pem: No such file
```

**Solution:** Run the Certbot initialization again (step 2-3)

### 502 Bad Gateway
```
**Causes:**
- App container not running
- Health check failing
- Database connection issue

**Debug:**
docker-compose logs app
docker-compose exec app curl http://localhost:5000/
```

### Certificate Renewal Failed
```bash
# Check Certbot logs
docker-compose logs certbot

# Manual renewal
docker-compose exec certbot certbot renew --verbose

# Force renewal
docker-compose exec certbot certbot renew --force-renewal
```

### DNS Not Resolving
```bash
# Verify DNS from server
nslookup nameinahat.com
dig nameinahat.com

# Should resolve to 172.233.185.208
```

## Maintenance

### Daily Certbot Renewal
The Certbot container runs a cron job at 3 AM UTC daily to check for certificate renewal. No manual intervention needed.

### Database Backups
```bash
# Create backup
docker-compose exec db pg_dump -U secret_santa secret_santa_db > backup.sql

# Restore backup
docker exec -i secret-santa-db-1 psql -U secret_santa secret_santa_db < backup.sql
```

### Update Application
```bash
# Pull latest code
cd /opt/secret-santa
git pull origin feature/https-migration

# Rebuild and restart
docker-compose up -d --build
```

## Security Checklist

- [ ] DNS configured: nameinahat.com → 172.233.185.208
- [ ] HTTPS certificate valid (check in browser)
- [ ] HTTP redirects to HTTPS
- [ ] Security headers present (HSTS, X-Frame-Options, etc.)
- [ ] Session cookies are HTTPS-only
- [ ] Certbot renewal working (check logs)
- [ ] Database password changed from default
- [ ] SECRET_KEY is unique and strong
- [ ] SMTP credentials are correct
- [ ] Firewall rules allow ports 80, 443 only (not 5000, 5432)

## Rollback to HTTP (if needed)

```bash
# Switch back to main branch
git checkout main

# Restart without HTTPS
docker-compose down
docker-compose up -d
```
