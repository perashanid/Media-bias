#!/usr/bin/env python3
"""
Investigate ATN News sitemap and try Somoy News alternatives
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def investigate_atn_sitemap():
    """Investigate ATN News sitemap for article URLs"""
    print("=== ATN News Sitemap Investigation ===")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get("https://www.atnnewstv.com/sitemap.xml", headers=headers, timeout=30)
        print(f"Sitemap status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            
            # Look for URL entries
            urls = soup.find_all('loc')
            print(f"Total URLs in sitemap: {len(urls)}")
            
            # Filter for potential article URLs
            article_urls = []
            for url_elem in urls:
                url = url_elem.get_text()
                
                # Look for patterns that suggest articles
                if any(pattern in url for pattern in ['/news/', '/article/', '/story/', '/details/', '/post/']):
                    article_urls.append(url)
                elif any(char.isdigit() for char in url.split('/')[-1]) and len(url.split('/')) > 4:
                    article_urls.append(url)
            
            print(f"Potential article URLs: {len(article_urls)}")
            
            # Show sample URLs
            for url in article_urls[:10]:
                print(f"  - {url}")
            
            # Test one article URL
            if article_urls:
                test_url = article_urls[0]
                print(f"\n--- Testing Article URL: {test_url} ---")
                
                try:
                    article_response = requests.get(test_url, headers=headers, timeout=30)
                    print(f"Article status: {article_response.status_code}")
                    
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        
                        # Test title
                        title = article_soup.find('title')
                        if title:
                            print(f"Title: {title.get_text()[:100]}...")
                        
                        # Test content selectors
                        content_selectors = [
                            '.content', '.article-content', '.news-content', 
                            '.story-content', 'article', '.post-content'
                        ]
                        
                        for selector in content_selectors:
                            content_elem = article_soup.select_one(selector)
                            if content_elem:
                                content_text = content_elem.get_text().strip()
                                if len(content_text) > 100:
                                    print(f"Content found with '{selector}': {len(content_text)} chars")
                                    print(f"Preview: {content_text[:150]}...")
                                    break
                        
                except Exception as e:
                    print(f"Error testing article: {e}")
            
            return article_urls
            
    except Exception as e:
        print(f"Sitemap error: {e}")
        return []

def try_somoy_alternatives():
    """Try alternative approaches for Somoy News"""
    print("\n=== Somoy News Alternative Approaches ===")
    
    alternatives = [
        "https://m.somoynews.tv",
        "https://mobile.somoynews.tv", 
        "https://www.somoynews.tv/rss",
        "https://www.somoynews.tv/feed",
        "https://www.somoynews.tv/sitemap.xml",
        "https://somoynews.tv/api",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for url in alternatives:
        print(f"\nTrying: {url}")
        try:
            time.sleep(random.uniform(2, 4))  # Longer delay
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Success! Content length: {len(response.content)}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"Title: {title.get_text()[:100]}...")
                
                # Look for article links
                links = soup.find_all('a', href=True)
                article_links = []
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    if href and text and len(text) > 10:
                        if any(pattern in href for pattern in ['/news/', '/article/', '/story/', '/details/', '/2025/', '/2024/']):
                            article_links.append((href, text[:50]))
                
                if article_links:
                    print(f"Article links found: {len(article_links)}")
                    for href, text in article_links[:5]:
                        print(f"  - {text}... -> {href}")
                    return True
                
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    """Main investigation"""
    # Investigate ATN News sitemap
    atn_urls = investigate_atn_sitemap()
    
    # Try Somoy News alternatives
    somoy_success = try_somoy_alternatives()
    
    print(f"\n=== Summary ===")
    print(f"ATN News: Found {len(atn_urls)} potential article URLs")
    print(f"Somoy News: {'Success' if somoy_success else 'Still blocked'}")

if __name__ == "__main__":
    main()