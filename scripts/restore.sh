#!/bin/bash

# Restore script for Media Bias Detector

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <backup_file.tar.gz>"
    echo "Available backups:"
    ls -la backups/media_bias_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="./restore_temp"

echo "🔄 Starting restore process..."
echo "📁 Backup file: $BACKUP_FILE"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env.development" ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
else
    echo "❌ No environment file found!"
    exit 1
fi

# Confirm restore operation
echo "⚠️  WARNING: This will overwrite the current database and configuration!"
echo "Database: ${MONGODB_DATABASE:-media_bias_detector}"
echo "Environment: ${FLASK_ENV:-unknown}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Create temporary restore directory
echo "📁 Creating temporary restore directory..."
rm -rf "$RESTORE_DIR"
mkdir -p "$RESTORE_DIR"

# Extract backup
echo "📦 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Find the backup directory
BACKUP_DIR=$(find "$RESTORE_DIR" -name "media_bias_backup_*" -type d | head -n 1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Invalid backup file structure"
    rm -rf "$RESTORE_DIR"
    exit 1
fi

echo "📋 Backup information:"
cat "$BACKUP_DIR/backup_info.txt" 2>/dev/null || echo "No backup info available"
echo ""

# Stop application services
echo "🛑 Stopping application services..."
docker-compose down 2>/dev/null || true

# Wait for services to stop
sleep 5

# Restore MongoDB
echo "🗄️  Restoring MongoDB..."
if [ -d "$BACKUP_DIR/mongodb" ]; then
    # Start only MongoDB for restore
    docker-compose up -d mongodb
    
    # Wait for MongoDB to be ready
    echo "⏳ Waiting for MongoDB to be ready..."
    sleep 15
    
    # Copy backup to MongoDB container
    docker cp "$BACKUP_DIR/mongodb" media-bias-mongodb:/tmp/
    
    # Restore database
    docker exec media-bias-mongodb mongorestore \
        --host localhost:27017 \
        --db ${MONGODB_DATABASE:-media_bias_detector} \
        --username ${MONGODB_USERNAME:-admin} \
        --password ${MONGODB_PASSWORD:-password} \
        --drop \
        /tmp/mongodb/${MONGODB_DATABASE:-media_bias_detector}
    
    # Clean up container
    docker exec media-bias-mongodb rm -rf /tmp/mongodb
    
    echo "✅ MongoDB restore completed"
else
    echo "⚠️  No MongoDB backup found in backup file"
fi

# Restore configuration files (optional)
echo "⚙️  Restoring configuration files..."
if [ -d "$BACKUP_DIR/config" ]; then
    read -p "Restore configuration files? (yes/no): " RESTORE_CONFIG
    if [ "$RESTORE_CONFIG" = "yes" ]; then
        cp -r "$BACKUP_DIR/config"/* config/ 2>/dev/null || true
        echo "✅ Configuration files restored"
    fi
fi

# Restore application data (optional)
echo "💾 Restoring application data..."
if [ -d "$BACKUP_DIR/data" ]; then
    read -p "Restore application data? (yes/no): " RESTORE_DATA
    if [ "$RESTORE_DATA" = "yes" ]; then
        rm -rf data
        cp -r "$BACKUP_DIR/data" . 2>/dev/null || true
        echo "✅ Application data restored"
    fi
fi

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -rf "$RESTORE_DIR"

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

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
    docker-compose ps
    echo "📋 Checking logs..."
    docker-compose logs --tail=50
    exit 1
fi

echo "✅ Restore completed successfully!"
echo ""
echo "📊 Application URLs:"
echo "   - Main application: http://localhost:${FLASK_PORT:-5000}"
echo "   - Health check: http://localhost:${FLASK_PORT:-5000}/health"
echo ""
echo "📋 Service status:"
docker-compose ps