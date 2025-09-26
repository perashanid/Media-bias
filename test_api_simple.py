#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

API_BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_bias_analysis():
    """Test bias analysis endpoint"""
    try:
        test_data = {
            "text": "This is an excellent government policy that will benefit everyone greatly.",
            "language": "english"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/bias/analyze-text",
            json=test_data,
            timeout=10
        )
        
        print(f"Bias analysis status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Bias analysis result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Bias analysis test failed: {e}")
        return False

def test_articles_endpoint():
    """Test articles endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/articles", timeout=5)
        print(f"Articles endpoint status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Articles count: {result.get('count', 0)}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Articles test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Media Bias Detection API...")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    # Test bias analysis
    print("\n2. Testing bias analysis...")
    bias_ok = test_bias_analysis()
    
    # Test articles endpoint
    print("\n3. Testing articles endpoint...")
    articles_ok = test_articles_endpoint()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health endpoint: {'✓' if health_ok else '✗'}")
    print(f"Bias analysis: {'✓' if bias_ok else '✗'}")
    print(f"Articles endpoint: {'✓' if articles_ok else '✗'}")
    
    if all([health_ok, bias_ok, articles_ok]):
        print("\n🎉 All API tests passed!")
    else:
        print("\n❌ Some tests failed.")