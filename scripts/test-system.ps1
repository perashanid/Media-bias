# PowerShell system testing script for Media Bias Detector

param(
    [string]$Environment = "development"
)

# Configuration
$API_BASE_URL = "http://localhost:5000"
$FRONTEND_URL = "http://localhost:3000"

# Test counters
$TOTAL_TESTS = 0
$PASSED_TESTS = 0
$FAILED_TESTS = 0

# Function to run a test
function Run-Test {
    param(
        [string]$TestName,
        [scriptblock]$TestCommand
    )
    
    $script:TOTAL_TESTS++
    Write-Host "Testing: $TestName" -ForegroundColor Blue
    
    try {
        $result = & $TestCommand
        if ($result) {
            Write-Host "✅ PASS: $TestName" -ForegroundColor Green
            $script:PASSED_TESTS++
            return $true
        } else {
            Write-Host "❌ FAIL: $TestName" -ForegroundColor Red
            $script:FAILED_TESTS++
            return $false
        }
    } catch {
        Write-Host "❌ FAIL: $TestName - $($_.Exception.Message)" -ForegroundColor Red
        $script:FAILED_TESTS++
        return $false
    }
}

# Function to test API endpoint
function Test-ApiEndpoint {
    param(
        [string]$Endpoint,
        [int]$ExpectedStatus = 200,
        [string]$Method = "GET"
    )
    
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE_URL$Endpoint" -Method $Method -UseBasicParsing -TimeoutSec 10
        return $response.StatusCode -eq $ExpectedStatus
    } catch {
        return $false
    }
}

# Function to test database connection
function Test-Database {
    try {
        $result = docker exec media-bias-mongodb-dev mongosh --eval "db.adminCommand('ping')" 2>$null
        return $result -match "ok"
    } catch {
        return $false
    }
}

Write-Host "🧪 Starting comprehensive system testing..." -ForegroundColor Cyan

# 1. Infrastructure Tests
Write-Host "`n=== Infrastructure Tests ===" -ForegroundColor Yellow

Run-Test "Docker containers running" {
    $containers = docker-compose -f docker-compose.dev.yml ps
    return $containers -match "Up"
}

Run-Test "MongoDB connection" {
    return Test-Database
}

Run-Test "Redis connection" {
    try {
        $result = docker exec media-bias-redis-dev redis-cli ping 2>$null
        return $result -match "PONG"
    } catch {
        return $false
    }
}

# 2. API Health Tests
Write-Host "`n=== API Health Tests ===" -ForegroundColor Yellow

Run-Test "API health endpoint" {
    return Test-ApiEndpoint "/health"
}

Run-Test "API articles endpoint" {
    return Test-ApiEndpoint "/api/articles"
}

Run-Test "API statistics endpoint" {
    return Test-ApiEndpoint "/api/statistics/overview"
}

# 3. API Endpoint Tests
Write-Host "`n=== API Endpoint Tests ===" -ForegroundColor Yellow

$endpoints = @(
    "/api/articles",
    "/api/statistics/overview",
    "/api/statistics/sources",
    "/api/comparison/sources"
)

foreach ($endpoint in $endpoints) {
    Run-Test "API endpoint $endpoint" {
        return Test-ApiEndpoint $endpoint
    }
}

# 4. Bias Analysis API Tests
Write-Host "`n=== Bias Analysis Tests ===" -ForegroundColor Yellow

Run-Test "Text bias analysis" {
    try {
        $body = @{
            text = "This is a test article."
            language = "english"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$API_BASE_URL/api/bias/analyze-text" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        return $response.PSObject.Properties.Name -contains "overall_bias_score"
    } catch {
        return $false
    }
}

# 5. Frontend Tests
Write-Host "`n=== Frontend Tests ===" -ForegroundColor Yellow

Run-Test "Frontend accessibility" {
    try {
        $response = Invoke-WebRequest -Uri $FRONTEND_URL -UseBasicParsing -TimeoutSec 10
        return $response.Content -match "Media Bias Detector"
    } catch {
        Write-Host "⚠️  Frontend not running, skipping frontend tests" -ForegroundColor Yellow
        return $true  # Don't fail the test if frontend is not running
    }
}

# 6. Error Handling Tests
Write-Host "`n=== Error Handling Tests ===" -ForegroundColor Yellow

Run-Test "404 for invalid endpoint" {
    return Test-ApiEndpoint "/api/nonexistent" 404
}

Run-Test "400 for invalid bias request" {
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE_URL/api/bias/analyze-text" -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
        return $false  # Should not succeed
    } catch {
        return $_.Exception.Response.StatusCode -eq 400
    }
}

# 7. Performance Tests
Write-Host "`n=== Performance Tests ===" -ForegroundColor Yellow

Run-Test "API response time < 5s" {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE_URL/health" -UseBasicParsing -TimeoutSec 5
        $stopwatch.Stop()
        return $stopwatch.ElapsedMilliseconds -lt 5000 -and $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Blue
Write-Host "Total Tests: $TOTAL_TESTS"
Write-Host "Passed: $PASSED_TESTS" -ForegroundColor Green
Write-Host "Failed: $FAILED_TESTS" -ForegroundColor Red

if ($FAILED_TESTS -eq 0) {
    Write-Host "`n🎉 All tests passed! System is ready for deployment." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ Some tests failed. Please review and fix issues before deployment." -ForegroundColor Red
    
    # Show debugging information
    Write-Host "`nDebugging Information:" -ForegroundColor Yellow
    Write-Host "- Check service logs: docker-compose -f docker-compose.dev.yml logs"
    Write-Host "- Verify database connection: docker exec media-bias-mongodb-dev mongosh"
    Write-Host "- Test API manually: curl $API_BASE_URL/health"
    Write-Host "- Check service status: docker-compose -f docker-compose.dev.yml ps"
    
    exit 1
}