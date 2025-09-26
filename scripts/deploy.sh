#!/bin/bash

# Deployment script for Media Bias Detector

set -e

echo "🚀 Starting deployment of Media Bias Detector..."

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.${ENVIRONMENT}"

if [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

echo "📋 Environment: $ENVIRONMENT"
echo "📋 Compose file: $COMPOSE_FILE"
echo "📋 Environment file: $ENV_FILE"

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found!"
    echo "Please create it based on .env.example"
    exit 1
fi

# Load environment variables
export $(cat $ENV_FILE | grep -v '^#' | xargs)

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data config/ssl

# Set proper permissions
chmod +x scripts/*.sh

# Build and start services
echo "🏗️  Building and starting services..."

if [ "$ENVIRONMENT" = "production" ]; then
    # Production deployment
    echo "🔧 Deploying to production..."
    
    # Pull latest images
    docker-compose -f $COMPOSE_FILE pull
    
    # Build application
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # Start services
    docker-compose -f $COMPOSE_FILE up -d
    
else
    # Development deployment
    echo "🔧 Deploying to development..."
    
    # Start services
    docker-compose -f $COMPOSE_FILE up -d --build
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🏥 Performing health check..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:${FLASK_PORT:-5000}/health > /dev/null 2>&1; then
        echo "✅ Application is healthy!"
        break
    else
        echo "⏳ Waiting for application to be ready... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
        sleep 10
        RETRY_COUNT=$((RETRY_COUNT + 1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Health check failed after $MAX_RETRIES attempts!"
    echo "📋 Checking service status..."
    docker-compose -f $COMPOSE_FILE ps
    echo "📋 Checking logs..."
    docker-compose -f $COMPOSE_FILE logs --tail=50
    exit 1
fi

# Show service status
echo "📋 Service status:"
docker-compose -f $COMPOSE_FILE ps

# Show useful information
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Application URLs:"
echo "   - Main application: http://localhost:${FLASK_PORT:-5000}"
echo "   - Health check: http://localhost:${FLASK_PORT:-5000}/health"
echo "   - API documentation: http://localhost:${FLASK_PORT:-5000}/api"
echo ""
echo "🗄️  Database:"
echo "   - MongoDB: localhost:${MONGODB_PORT:-27017}"
echo "   - Database name: ${MONGODB_DATABASE:-media_bias_detector}"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "   - Stop services: docker-compose -f $COMPOSE_FILE down"
echo "   - Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "   - Update services: ./scripts/deploy.sh $ENVIRONMENT"
echo ""

if [ "$ENVIRONMENT" = "production" ]; then
    echo "⚠️  Production deployment notes:"
    echo "   - Update passwords in $ENV_FILE"
    echo "   - Configure SSL certificates in config/ssl/"
    echo "   - Set up proper DNS and firewall rules"
    echo "   - Configure email alerts for monitoring"
    echo "   - Set up regular backups for MongoDB"
fi