#!/usr/bin/env python3
"""
Test the complete scraping and storage workflow
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import requests
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_url_scraping():
    """Test URL scraping via API"""
    print("🔧 Testing URL scraping...")
    
    # Test URL (using a reliable news site)
    test_url = "https://www.bbc.com/news"
    
    try:
        response = requests.post(
            "http://localhost:5000/api/scrape/manual",
            json={"url": test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ URL scraping successful: {data.get('message')}")
                print(f"   Article ID: {data.get('article_id')}")
                print(f"   Title: {data.get('title', 'N/A')}")
                return data.get('article_id')
            else:
                print(f"❌ URL scraping failed: {data.get('error')}")
        else:
            print(f"❌ URL scraping failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ URL scraping error: {e}")
    
    return None

def test_source_scraping():
    """Test source scraping via API"""
    print("🔧 Testing source scraping...")
    
    try:
        # First get available sources
        sources_response = requests.get("http://localhost:5000/api/scrape/sources", timeout=10)
        if sources_response.status_code != 200:
            print("❌ Failed to get available sources")
            return None
        
        sources_data = sources_response.json()
        sources = sources_data.get('sources', [])
        
        if not sources:
            print("❌ No sources available")
            return None
        
        # Test scraping from first source
        test_source = sources[0]
        print(f"   Testing source: {test_source}")
        
        response = requests.post(
            "http://localhost:5000/api/scrape/manual",
            json={"source": test_source},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Source scraping successful: {data.get('message')}")
                print(f"   Articles stored: {data.get('articles_count', 0)}")
                print(f"   Articles analyzed: {data.get('analyzed_count', 0)}")
                return data.get('articles_count', 0)
            else:
                print(f"❌ Source scraping failed: {data.get('error')}")
        else:
            print(f"❌ Source scraping failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Source scraping error: {e}")
    
    return None

def test_articles_retrieval():
    """Test retrieving articles via API"""
    print("🔧 Testing articles retrieval...")
    
    try:
        response = requests.get("http://localhost:5000/api/articles?limit=10", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            count = len(articles)
            
            print(f"✅ Retrieved {count} articles")
            
            if count > 0:
                # Show details of first article
                first_article = articles[0]
                print(f"   Sample article:")
                print(f"     Title: {first_article.get('title', 'N/A')[:50]}...")
                print(f"     Source: {first_article.get('source', 'N/A')}")
                print(f"     ID: {first_article.get('id', 'N/A')}")
                print(f"     Has bias scores: {'bias_scores' in first_article}")
            
            return count
        else:
            print(f"❌ Articles retrieval failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Articles retrieval error: {e}")
    
    return 0

def test_statistics():
    """Test statistics endpoint"""
    print("🔧 Testing statistics...")
    
    try:
        response = requests.get("http://localhost:5000/api/statistics/overview", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics retrieved:")
            print(f"   Total articles: {data.get('total_articles', 0)}")
            print(f"   Analyzed articles: {data.get('analyzed_articles', 0)}")
            print(f"   Recent articles: {data.get('recent_articles', 0)}")
            print(f"   Source counts: {data.get('source_counts', {})}")
            return True
        else:
            print(f"❌ Statistics failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    return False

def main():
    """Run complete workflow test"""
    print("🎯 Complete Workflow Test")
    print("=" * 50)
    print("⚠️  Make sure the backend is running (npm run backend)")
    print()
    
    # Test individual components
    url_result = test_url_scraping()
    print()
    
    source_result = test_source_scraping()
    print()
    
    articles_count = test_articles_retrieval()
    print()
    
    stats_result = test_statistics()
    print()
    
    # Summary
    print("📋 Test Summary:")
    print(f"   URL Scraping: {'✅' if url_result else '❌'}")
    print(f"   Source Scraping: {'✅' if source_result else '❌'}")
    print(f"   Articles Retrieved: {articles_count}")
    print(f"   Statistics: {'✅' if stats_result else '❌'}")
    
    if articles_count > 0:
        print("\n🎉 Workflow is working! Articles are being scraped and stored.")
        print("   You should see these articles in the frontend Articles section.")
    else:
        print("\n⚠️  No articles found. Check the scraping functionality.")

if __name__ == "__main__":
    main()