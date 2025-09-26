"""
Integration tests for Media Bias Detector system
"""

import pytest
import requests
import time
from datetime import datetime
import uuid

# Test configuration
API_BASE_URL = "http://localhost:5000"
TEST_TIMEOUT = 30


class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_articles_endpoint(self):
        """Test articles API endpoint"""
        response = requests.get(f"{API_BASE_URL}/api/articles", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert isinstance(data["articles"], list)
    
    def test_statistics_endpoint(self):
        """Test statistics API endpoint"""
        response = requests.get(f"{API_BASE_URL}/api/statistics/overview", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data
        assert isinstance(data["total_articles"], int)
    
    def test_bias_analysis_endpoint(self):
        """Test bias analysis API endpoint"""
        test_data = {
            "text": "This is a test article about politics and government policies.",
            "language": "english"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json=test_data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "overall_bias_score",
            "sentiment_score",
            "political_bias_score",
            "emotional_language_score",
            "factual_vs_opinion_score"
        ]
        
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
    
    def test_bias_analysis_bengali(self):
        """Test bias analysis with Bengali text"""
        test_data = {
            "text": "সরকারের এই নতুন নীতি দেশের উন্নয়নে সহায়ক হবে।",
            "language": "bengali"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json=test_data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_bias_score" in data
        assert data["language"] == "bengali"
    
    def test_invalid_bias_analysis(self):
        """Test bias analysis with invalid data"""
        # Empty text should return 400
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={},
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 400
    
    def test_source_comparison(self):
        """Test source comparison endpoint"""
        response = requests.get(
            f"{API_BASE_URL}/api/comparison/sources",
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert "source_comparison" in data
    
    def test_article_search(self):
        """Test article search functionality"""
        response = requests.get(
            f"{API_BASE_URL}/api/articles/search?q=test",
            timeout=TEST_TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "count" in data
    
    def test_nonexistent_endpoint(self):
        """Test 404 for nonexistent endpoint"""
        response = requests.get(f"{API_BASE_URL}/api/nonexistent")
        assert response.status_code == 404
    
    def test_api_response_time(self):
        """Test API response time"""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=TEST_TIMEOUT)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds


class TestBiasAnalysisAccuracy:
    """Tests for bias analysis accuracy"""
    
    def test_positive_sentiment_detection(self):
        """Test detection of positive sentiment"""
        test_text = "This is an excellent and wonderful achievement that brings great joy and happiness to everyone."
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={"text": test_text, "language": "english"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment_score"] > 0.1  # Should detect positive sentiment
    
    def test_negative_sentiment_detection(self):
        """Test detection of negative sentiment"""
        test_text = "This is a terrible and awful situation that causes great pain and suffering to many people."
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={"text": test_text, "language": "english"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment_score"] < -0.1  # Should detect negative sentiment
    
    def test_factual_content_detection(self):
        """Test detection of factual content"""
        test_text = "According to official statistics, the GDP grew by 3.2% last year. The report was published yesterday."
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={"text": test_text, "language": "english"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["factual_vs_opinion_score"] > 0.5  # Should detect factual content
    
    def test_opinion_content_detection(self):
        """Test detection of opinion content"""
        test_text = "I think this policy is wrong and the government should reconsider. In my opinion, this is a bad decision."
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={"text": test_text, "language": "english"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["factual_vs_opinion_score"] < 0.5  # Should detect opinion content


class TestSystemPerformance:
    """Performance tests for the system"""
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            response = requests.get(f"{API_BASE_URL}/health", timeout=TEST_TIMEOUT)
            return response.status_code == 200
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(results)
    
    def test_large_text_analysis(self):
        """Test bias analysis with large text"""
        # Create a large text (about 5000 words)
        large_text = " ".join([
            "This is a test sentence about politics and government policies."
        ] * 500)
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json={"text": large_text, "language": "english"},
            timeout=60  # Longer timeout for large text
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_bias_score" in data


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])