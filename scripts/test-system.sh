#!/bin/bash

# Comprehensive system testing script for Media Bias Detector

set -e

echo "🧪 Starting comprehensive system testing..."

# Configuration
TEST_ENV="development"
API_BASE_URL="http://localhost:5000"
FRONTEND_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}Testing: $test_name${NC}"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint="$1"
    local expected_status="${2:-200}"
    local method="${3:-GET}"
    
    if [ "$method" = "GET" ]; then
        curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL$endpoint" | grep -q "$expected_status"
    else
        curl -s -o /dev/null -w "%{http_code}" -X "$method" "$API_BASE_URL$endpoint" | grep -q "$expected_status"
    fi
}

# Function to test database connection
test_database() {
    # Check if MongoDB container is running and accessible
    docker exec media-bias-mongodb-dev mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1
}

# Function to test scraper functionality
test_scraper() {
    # Test scraper manager initialization
    python3 -c "
from scrapers.scraper_manager import ScraperManager
manager = ScraperManager()
sources = manager.get_available_sources()
assert len(sources) == 5, f'Expected 5 sources, got {len(sources)}'
print('Scraper manager test passed')
" 2>/dev/null
}

# Function to test bias analyzer
test_bias_analyzer() {
    # Test bias analysis with sample text
    python3 -c "
from services.bias_analyzer import BiasAnalyzer
analyzer = BiasAnalyzer()
result = analyzer.analyze_text_sample('This is a test article about politics.', 'english')
assert 'overall_bias_score' in result, 'Missing overall_bias_score'
assert 'sentiment_score' in result, 'Missing sentiment_score'
print('Bias analyzer test passed')
" 2>/dev/null
}

# Function to test article storage
test_article_storage() {
    # Test article storage service
    python3 -c "
from services.article_storage_service import ArticleStorageService
from models.article import Article
from datetime import datetime
import hashlib

storage = ArticleStorageService()
stats = storage.get_storage_statistics()
assert isinstance(stats, dict), 'Storage statistics should be a dict'
print('Article storage test passed')
" 2>/dev/null
}

echo "🚀 Starting system tests..."

# 1. Infrastructure Tests
echo -e "\n${YELLOW}=== Infrastructure Tests ===${NC}"

run_test "Docker containers running" "docker-compose -f docker-compose.dev.yml ps | grep -q 'Up'"
run_test "MongoDB connection" "test_database"
run_test "Redis connection" "docker exec media-bias-redis-dev redis-cli ping | grep -q PONG"

# 2. API Health Tests
echo -e "\n${YELLOW}=== API Health Tests ===${NC}"

run_test "API health endpoint" "test_api_endpoint '/health' 200"
run_test "API articles endpoint" "test_api_endpoint '/api/articles' 200"
run_test "API statistics endpoint" "test_api_endpoint '/api/statistics/overview' 200"

# 3. Core Service Tests
echo -e "\n${YELLOW}=== Core Service Tests ===${NC}"

run_test "Scraper manager initialization" "test_scraper"
run_test "Bias analyzer functionality" "test_bias_analyzer"
run_test "Article storage service" "test_article_storage"

# 4. API Endpoint Tests
echo -e "\n${YELLOW}=== API Endpoint Tests ===${NC}"

# Test all major API endpoints
endpoints=(
    "/api/articles"
    "/api/statistics/overview"
    "/api/statistics/sources"
    "/api/comparison/sources"
)

for endpoint in "${endpoints[@]}"; do
    run_test "API endpoint $endpoint" "test_api_endpoint '$endpoint' 200"
done

# 5. Bias Analysis API Tests
echo -e "\n${YELLOW}=== Bias Analysis Tests ===${NC}"

# Test bias analysis with sample text
run_test "Text bias analysis" "curl -s -X POST '$API_BASE_URL/api/bias/analyze-text' \
    -H 'Content-Type: application/json' \
    -d '{\"text\": \"This is a test article.\", \"language\": \"english\"}' \
    | grep -q 'overall_bias_score'"

# 6. Database Integration Tests
echo -e "\n${YELLOW}=== Database Integration Tests ===${NC}"

# Test database operations
run_test "Database article insertion" "python3 -c \"
from services.article_storage_service import ArticleStorageService
from models.article import Article
from datetime import datetime
import uuid

storage = ArticleStorageService()
test_article = Article(
    url=f'http://test.com/{uuid.uuid4()}',
    title='Test Article',
    content='This is a test article content.',
    source='Test Source',
    publication_date=datetime.now(),
    scraped_at=datetime.now(),
    language='english'
)

article_id = storage.store_article(test_article)
assert article_id is not None, 'Failed to store test article'
print('Database integration test passed')
\""

# 7. Frontend Tests (if available)
echo -e "\n${YELLOW}=== Frontend Tests ===${NC}"

if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    run_test "Frontend accessibility" "curl -s '$FRONTEND_URL' | grep -q 'Media Bias Detector'"
else
    echo -e "${YELLOW}⚠️  Frontend not running, skipping frontend tests${NC}"
fi

# 8. End-to-End Workflow Tests
echo -e "\n${YELLOW}=== End-to-End Workflow Tests ===${NC}"

# Test complete workflow: scrape -> store -> analyze -> compare
run_test "Complete workflow simulation" "python3 -c \"
import sys
sys.path.append('.')

from scrapers.scraper_manager import ScraperManager
from services.article_storage_service import ArticleStorageService
from services.bias_analyzer import BiasAnalyzer
from models.article import Article
from datetime import datetime
import uuid

# Create test article
test_article = Article(
    url=f'http://workflow-test.com/{uuid.uuid4()}',
    title='Workflow Test Article',
    content='This is a comprehensive test of the complete workflow system.',
    source='Test Source',
    publication_date=datetime.now(),
    scraped_at=datetime.now(),
    language='english'
)

# Store article
storage = ArticleStorageService()
article_id = storage.store_article(test_article)
assert article_id, 'Failed to store article'

# Analyze bias
analyzer = BiasAnalyzer()
bias_scores = analyzer.analyze_article_bias(test_article)
assert bias_scores, 'Failed to analyze bias'

# Update with bias scores
success = storage.update_article_bias_scores(article_id, bias_scores.to_dict())
assert success, 'Failed to update bias scores'

print('End-to-end workflow test passed')
\""

# 9. Performance Tests
echo -e "\n${YELLOW}=== Performance Tests ===${NC}"

# Test API response times
run_test "API response time < 2s" "timeout 2s curl -s '$API_BASE_URL/health' > /dev/null"

# Test concurrent requests
run_test "Concurrent API requests" "
for i in {1..5}; do
    curl -s '$API_BASE_URL/health' > /dev/null &
done
wait
"

# 10. Error Handling Tests
echo -e "\n${YELLOW}=== Error Handling Tests ===${NC}"

# Test invalid endpoints
run_test "404 for invalid endpoint" "test_api_endpoint '/api/nonexistent' 404"

# Test invalid bias analysis request
run_test "400 for invalid bias request" "curl -s -o /dev/null -w '%{http_code}' \
    -X POST '$API_BASE_URL/api/bias/analyze-text' \
    -H 'Content-Type: application/json' \
    -d '{}' | grep -q '400'"

# 11. Security Tests
echo -e "\n${YELLOW}=== Security Tests ===${NC}"

# Test CORS headers
run_test "CORS headers present" "curl -s -I '$API_BASE_URL/health' | grep -q 'Access-Control'"

# Test input validation
run_test "SQL injection protection" "curl -s -o /dev/null -w '%{http_code}' \
    '$API_BASE_URL/api/articles?source=test%27%20OR%20%271%27=%271' | grep -q '200'"

# Summary
echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! System is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review and fix issues before deployment.${NC}"
    
    # Show failed test details
    echo -e "\n${YELLOW}Debugging Information:${NC}"
    echo "- Check service logs: docker-compose -f docker-compose.dev.yml logs"
    echo "- Verify database connection: docker exec media-bias-mongodb-dev mongosh"
    echo "- Test API manually: curl $API_BASE_URL/health"
    echo "- Check service status: docker-compose -f docker-compose.dev.yml ps"
    
    exit 1
fi