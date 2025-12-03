#!/bin/bash
set -e

echo "=== Secret Santa Server Setup ==="
echo "This script installs all dependencies for running the Secret Santa container"
echo ""

# Update system packages
echo "1. Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "2. Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "3. Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
echo "4. Configuring Docker user permissions..."
sudo usermod -aG docker $USER
echo "Note: You may need to log out and back in for group changes to take effect"

# Install Git
echo "5. Installing Git..."
sudo apt-get install -y git

# Install other useful tools
echo "6. Installing additional tools..."
sudo apt-get install -y curl wget vim nano htop

# Create app directory
echo "7. Creating application directory..."
sudo mkdir -p /opt/secret-santa
sudo chown $USER:$USER /opt/secret-santa

# Create directories for persistent data
echo "8. Creating data directories..."
mkdir -p /opt/secret-santa/postgres-data
mkdir -p /opt/secret-santa/certbot-certs
mkdir -p /opt/secret-santa/certbot-conf
mkdir -p /opt/secret-santa/nginx-conf

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Clone the repository: cd /opt/secret-santa && git clone https://github.com/cmsgraham/secret-santa.git ."
echo "2. Copy docker-compose.yml and other files to /opt/secret-santa"
echo "3. Configure environment variables in .env"
echo "4. Run: docker-compose up -d"
echo ""
echo "You may need to log out and back in for Docker group changes to take effect."
