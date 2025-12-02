# Server Setup Guide for 172.233.185.208

## Quick Setup (Automated)

Run this on the new server:

```bash
# SSH into the server
ssh root@172.233.185.208

# Download and run setup script
curl -O https://raw.githubusercontent.com/cmsgraham/secret-santa/main/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

## Manual Setup (If needed)

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Docker
```bash
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

### 3. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. Configure Docker Permissions
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### 5. Install Git
```bash
sudo apt-get install -y git
```

### 6. Create Application Directory
```bash
sudo mkdir -p /opt/secret-santa
sudo chown $USER:$USER /opt/secret-santa
cd /opt/secret-santa
```

### 7. Clone Repository
```bash
git clone https://github.com/cmsgraham/secret-santa.git .
```

### 8. Create Required Directories
```bash
mkdir -p postgres-data certbot-certs certbot-conf nginx-conf
```

### 9. Verify Installation
```bash
docker --version
docker-compose --version
git --version
```

## Expected Output

- Docker version 20.10+ 
- Docker Compose version 2.0+
- git version 2.x+

## Troubleshooting

**Docker permission denied:**
```bash
# Already added to group, but need to activate
newgrp docker
```

**Port conflicts (80, 443, 5000, 5432):**
```bash
# Check what's using ports
sudo netstat -tulpn | grep LISTEN
```

**DNS resolution issues:**
```bash
# Add to /etc/hosts if needed
echo "172.233.185.208 nameinahat.com" | sudo tee -a /etc/hosts
```

## What Gets Installed

| Component | Purpose |
|-----------|---------|
| Docker | Container runtime |
| Docker Compose | Multi-container orchestration |
| Git | Version control, clone repo |
| curl, wget | Download tools |
| vim, nano | Text editors |
| htop | System monitoring |

## Next Steps

1. **Set up environment variables** (create `.env` file)
2. **Configure docker-compose.yml** with Nginx service
3. **Generate SSL certificates** with Certbot
4. **Deploy the application** with `docker-compose up -d`
5. **Verify all services** are running

Ready to proceed?
