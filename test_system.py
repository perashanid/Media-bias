#!/usr/bin/env python3
"""
Simple system test script to verify all components are working
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE = "http://localhost:5000"

def test_api_endpoints():
    """Test basic API endpoints"""
    print("Testing API endpoints...")
    
    endpoints = [
        "/health",
        "/api/articles",
        "/api/statistics/overview",
        "/api/comparison/sources",
        "/api/scrape/sources"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"  {status} {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"  ✗ {endpoint} - Error: {e}")

def test_custom_comparison():
    """Test the custom comparison feature"""
    print("\nTesting custom comparison...")
    
    test_data = {
        'inputs': [
            {
                'type': 'text',
                'value': 'The government announced new policies today. These changes will benefit all citizens and improve the economy significantly.',
                'title': 'Positive Government News',
                'source': 'Test Source A'
            },
            {
                'type': 'text', 
                'value': 'The government announced new policies today. Critics argue these changes will harm citizens and damage the economy.',
                'title': 'Critical Government News',
                'source': 'Test Source B'
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/comparison/custom",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Custom comparison successful")
            print(f"    - Articles processed: {len(result.get('articles', []))}")
            print(f"    - Story ID: {result.get('story_id')}")
            print(f"    - Key differences: {len(result.get('key_differences', []))}")
        else:
            print(f"  ✗ Custom comparison failed: {response.status_code}")
            print(f"    Error: {response.json()}")
            
    except Exception as e:
        print(f"  ✗ Custom comparison error: {e}")

def test_bias_analysis():
    """Test bias analysis on sample text"""
    print("\nTesting bias analysis...")
    
    test_text = "This is a completely neutral news article about recent events. The facts are presented objectively without any bias."
    
    try:
        response = requests.post(
            f"{API_BASE}/api/bias/analyze-text",
            json={'text': test_text},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Bias analysis successful")
            print(f"    - Overall bias: {result.get('overall_bias_score', 'N/A')}")
            print(f"    - Sentiment: {result.get('sentiment_score', 'N/A')}")
        else:
            print(f"  ✗ Bias analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Bias analysis error: {e}")

def main():
    print("=" * 50)
    print("Media Bias Detector - System Test")
    print("=" * 50)
    print(f"Testing at: {datetime.now()}")
    print(f"API Base: {API_BASE}")
    print()
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_api_endpoints()
    test_custom_comparison()
    test_bias_analysis()
    
    print("\n" + "=" * 50)
    print("System test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()