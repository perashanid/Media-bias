#!/bin/bash

# Backup script for Media Bias Detector

set -e

echo "💾 Starting backup process..."

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="media_bias_backup_${TIMESTAMP}"

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env.development" ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
else
    echo "❌ No environment file found!"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📁 Backup directory: $BACKUP_DIR/$BACKUP_NAME"

# Create backup subdirectory
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$FULL_BACKUP_PATH"

# Backup MongoDB
echo "🗄️  Backing up MongoDB..."
if docker ps | grep -q "media-bias-mongodb"; then
    # MongoDB is running in Docker
    docker exec media-bias-mongodb mongodump \
        --host localhost:27017 \
        --db ${MONGODB_DATABASE:-media_bias_detector} \
        --username ${MONGODB_USERNAME:-admin} \
        --password ${MONGODB_PASSWORD:-password} \
        --out /tmp/backup
    
    # Copy backup from container
    docker cp media-bias-mongodb:/tmp/backup "$FULL_BACKUP_PATH/mongodb"
    
    # Clean up container backup
    docker exec media-bias-mongodb rm -rf /tmp/backup
else
    # MongoDB is running locally
    mongodump \
        --host ${MONGODB_HOST:-localhost}:${MONGODB_PORT:-27017} \
        --db ${MONGODB_DATABASE:-media_bias_detector} \
        --username ${MONGODB_USERNAME:-admin} \
        --password ${MONGODB_PASSWORD:-password} \
        --out "$FULL_BACKUP_PATH/mongodb"
fi

# Backup configuration files
echo "⚙️  Backing up configuration files..."
mkdir -p "$FULL_BACKUP_PATH/config"
cp -r config/* "$FULL_BACKUP_PATH/config/" 2>/dev/null || true
cp .env.* "$FULL_BACKUP_PATH/" 2>/dev/null || true
cp docker-compose*.yml "$FULL_BACKUP_PATH/" 2>/dev/null || true

# Backup logs (last 7 days)
echo "📝 Backing up recent logs..."
if [ -d "logs" ]; then
    mkdir -p "$FULL_BACKUP_PATH/logs"
    find logs -name "*.log" -mtime -7 -exec cp {} "$FULL_BACKUP_PATH/logs/" \; 2>/dev/null || true
fi

# Backup application data
echo "💾 Backing up application data..."
if [ -d "data" ]; then
    cp -r data "$FULL_BACKUP_PATH/" 2>/dev/null || true
fi

# Create backup metadata
echo "📋 Creating backup metadata..."
cat > "$FULL_BACKUP_PATH/backup_info.txt" << EOF
Media Bias Detector Backup
==========================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Database: ${MONGODB_DATABASE:-media_bias_detector}
Environment: ${FLASK_ENV:-unknown}

Contents:
- MongoDB database dump
- Configuration files
- Recent logs (last 7 days)
- Application data

Restore Instructions:
1. Stop the application: docker-compose down
2. Restore MongoDB: mongorestore --drop mongodb/${MONGODB_DATABASE:-media_bias_detector}
3. Restore configuration files as needed
4. Start the application: docker-compose up -d
EOF

# Compress backup
echo "🗜️  Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)

echo "✅ Backup completed successfully!"
echo "📁 Backup file: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📏 Backup size: $BACKUP_SIZE"

# Cleanup old backups (keep last 10)
echo "🧹 Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t media_bias_backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "💾 Backup process completed!"

# Optional: Upload to cloud storage
if [ ! -z "$BACKUP_UPLOAD_COMMAND" ]; then
    echo "☁️  Uploading backup to cloud storage..."
    eval "$BACKUP_UPLOAD_COMMAND $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
fi