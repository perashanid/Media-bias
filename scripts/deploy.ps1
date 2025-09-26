# PowerShell deployment script for Media Bias Detector

param(
    [string]$Environment = "production"
)

Write-Host "🚀 Starting deployment of Media Bias Detector..." -ForegroundColor Green

# Configuration
$ComposeFile = "docker-compose.yml"
$EnvFile = ".env.$Environment"

if ($Environment -eq "development") {
    $ComposeFile = "docker-compose.dev.yml"
}

Write-Host "📋 Environment: $Environment" -ForegroundColor Cyan
Write-Host "📋 Compose file: $ComposeFile" -ForegroundColor Cyan
Write-Host "📋 Environment file: $EnvFile" -ForegroundColor Cyan

# Check if environment file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Environment file $EnvFile not found!" -ForegroundColor Red
    Write-Host "Please create it based on .env.example" -ForegroundColor Yellow
    exit 1
}

# Pre-deployment checks
Write-Host "🔍 Running pre-deployment checks..." -ForegroundColor Yellow

# Check Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed or not in PATH!" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Docker Compose is not installed or not in PATH!" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs", "data", "config/ssl" | Out-Null

# Build and start services
Write-Host "🏗️  Building and starting services..." -ForegroundColor Yellow

if ($Environment -eq "production") {
    # Production deployment
    Write-Host "🔧 Deploying to production..." -ForegroundColor Cyan
    
    # Pull latest images
    docker-compose -f $ComposeFile pull
    
    # Build application
    docker-compose -f $ComposeFile build --no-cache
    
    # Start services
    docker-compose -f $ComposeFile up -d
} else {
    # Development deployment
    Write-Host "🔧 Deploying to development..." -ForegroundColor Cyan
    
    # Start services
    docker-compose -f $ComposeFile up -d --build
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Health check
Write-Host "🏥 Performing health check..." -ForegroundColor Yellow
$MaxRetries = 10
$RetryCount = 0
$FlaskPort = 5000

# Load environment variables to get port
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "FLASK_PORT=(.+)") {
            $FlaskPort = $matches[1]
        }
    }
}

while ($RetryCount -lt $MaxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$FlaskPort/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Application is healthy!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "⏳ Waiting for application to be ready... (attempt $($RetryCount + 1)/$MaxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        $RetryCount++
    }
}

if ($RetryCount -eq $MaxRetries) {
    Write-Host "❌ Health check failed after $MaxRetries attempts!" -ForegroundColor Red
    Write-Host "📋 Checking service status..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile ps
    Write-Host "📋 Checking logs..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile logs --tail=50
    exit 1
}

# Show service status
Write-Host "📋 Service status:" -ForegroundColor Cyan
docker-compose -f $ComposeFile ps

# Show useful information
Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Application URLs:" -ForegroundColor Cyan
Write-Host "   - Main application: http://localhost:$FlaskPort" -ForegroundColor White
Write-Host "   - Health check: http://localhost:$FlaskPort/health" -ForegroundColor White
Write-Host "   - API documentation: http://localhost:$FlaskPort/api" -ForegroundColor White
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Cyan
Write-Host "   - View logs: docker-compose -f $ComposeFile logs -f" -ForegroundColor White
Write-Host "   - Stop services: docker-compose -f $ComposeFile down" -ForegroundColor White
Write-Host "   - Restart services: docker-compose -f $ComposeFile restart" -ForegroundColor White
Write-Host "   - Update services: .\scripts\deploy.ps1 $Environment" -ForegroundColor White
Write-Host ""

if ($Environment -eq "production") {
    Write-Host "⚠️  Production deployment notes:" -ForegroundColor Yellow
    Write-Host "   - Update passwords in $EnvFile" -ForegroundColor White
    Write-Host "   - Configure SSL certificates in config/ssl/" -ForegroundColor White
    Write-Host "   - Set up proper DNS and firewall rules" -ForegroundColor White
    Write-Host "   - Configure email alerts for monitoring" -ForegroundColor White
    Write-Host "   - Set up regular backups for MongoDB" -ForegroundColor White
}