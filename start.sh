#!/bin/bash

# Secret Santa Application - WhatsApp Version Quick Start

set -e

echo "🎅 Secret Santa Application - WhatsApp Edition"
echo "============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i.bak "s/SECRET_KEY=change-this-to-a-random-secret-key-for-production/SECRET_KEY=$SECRET_KEY/" .env
    rm .env.bak
    
    echo "⚠️  IMPORTANT: Configure WhatsApp Business API credentials in .env file!"
    echo "📱 Required WhatsApp settings:"
    echo "   - WHATSAPP_ACCESS_TOKEN (from Meta Developer Console)"
    echo "   - WHATSAPP_PHONE_NUMBER_ID (from WhatsApp Business API)"
    echo "   - DEFAULT_SENDER_EMAIL (organizer contact email)"
    echo ""
    echo "📖 See WHATSAPP_SETUP.md for detailed setup instructions"
    echo ""
    read -p "Press Enter to continue after configuring WhatsApp credentials..."
fi

# Build and start the application
echo "🏗️  Building and starting Secret Santa WhatsApp application..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "❌ Application health check failed. Checking logs..."
    docker-compose logs app
    exit 1
fi

echo ""
echo "🎉 Secret Santa WhatsApp application is now running!"
echo "================================================="
echo "🌐 Web Interface: http://localhost:5000"
echo "🔍 Health Check: http://localhost:5000/health"
echo "📱 Messages: Delivered via WhatsApp Business API"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f app"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"
echo ""
echo "📚 For WhatsApp setup, see WHATSAPP_SETUP.md"