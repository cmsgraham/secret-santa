#!/bin/bash
# Build and push Secret Santa app to DockerHub
# Usage: ./build-and-push.sh [version]

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-cmsgraham}"
DOCKER_REPO="secret-santa"
VERSION="${1:-latest}"
IMAGE_NAME="${DOCKER_USERNAME}/${DOCKER_REPO}:${VERSION}"
LATEST_IMAGE_NAME="${DOCKER_USERNAME}/${DOCKER_REPO}:latest"

echo "🚀 Building Secret Santa Docker image..."
echo "   Image: $IMAGE_NAME"
echo "   Also tagging as: $LATEST_IMAGE_NAME"

# Build the image
docker build -t "$IMAGE_NAME" -t "$LATEST_IMAGE_NAME" .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed!"
    exit 1
fi

# Check if user is logged in to Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running or you're not logged in"
    echo "Please run: docker login"
    exit 1
fi

echo ""
echo "📤 Pushing to DockerHub..."
docker push "$IMAGE_NAME"
docker push "$LATEST_IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Push successful!"
    echo ""
    echo "📋 Image Details:"
    echo "   Full image: $IMAGE_NAME"
    echo "   Latest tag: $LATEST_IMAGE_NAME"
    echo ""
    echo "🎯 To deploy on your server, pull the image:"
    echo "   docker pull $IMAGE_NAME"
else
    echo "❌ Push failed!"
    exit 1
fi
