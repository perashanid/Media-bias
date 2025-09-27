#!/usr/bin/env python3
"""
Test the articles API endpoint
"""

import requests
import json

def test_articles_api():
    """Test the articles API endpoint"""
    try:
        print("🔧 Testing articles API...")
        
        response = requests.get("http://localhost:5000/api/articles", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            count = len(articles)
            
            print(f"✅ API returned {count} articles")
            
            if count > 0:
                print("\n📄 Sample articles:")
                for i, article in enumerate(articles[:3]):  # Show first 3
                    print(f"   {i+1}. {article.get('title', 'No title')[:60]}...")
                    print(f"      Source: {article.get('source', 'Unknown')}")
                    print(f"      ID: {article.get('id', 'No ID')}")
                    print(f"      Has bias scores: {'bias_scores' in article}")
                    print()
            
            return count > 0
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_statistics_api():
    """Test the statistics API endpoint"""
    try:
        print("🔧 Testing statistics API...")
        
        response = requests.get("http://localhost:5000/api/statistics/overview", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics API working:")
            print(f"   Total articles: {data.get('total_articles', 0)}")
            print(f"   Analyzed articles: {data.get('analyzed_articles', 0)}")
            print(f"   Source counts: {data.get('source_counts', {})}")
            return True
        else:
            print(f"❌ Statistics API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Statistics API test failed: {e}")
        return False

def main():
    """Run API tests"""
    print("🎯 API Test - Articles Endpoint")
    print("=" * 50)
    print("⚠️  Make sure the backend is running on localhost:5000")
    print()
    
    articles_ok = test_articles_api()
    print()
    stats_ok = test_statistics_api()
    
    print("\n📋 Results:")
    print(f"   Articles API: {'✅' if articles_ok else '❌'}")
    print(f"   Statistics API: {'✅' if stats_ok else '❌'}")
    
    if articles_ok:
        print("\n🎉 Articles are available via API!")
        print("   They should now appear in the frontend Articles section.")
    else:
        print("\n❌ No articles found via API.")

if __name__ == "__main__":
    main()