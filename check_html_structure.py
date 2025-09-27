#!/usr/bin/env python3
"""
Check actual HTML structure of Daily Star pages
"""

import requests
from bs4 import BeautifulSoup

def check_html_structure():
    """Check HTML structure"""
    urls = [
        "https://www.thedailystar.net",
        "https://www.thedailystar.net/news/bangladesh"
    ]
    
    for url in urls:
        print(f"\n{'='*50}")
        print(f"Checking: {url}")
        print('='*50)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check all links
        all_links = soup.find_all('a', href=True)
        print(f"Total links: {len(all_links)}")
        
        # Check for news links specifically
        news_links = [link for link in all_links if '/news/' in link.get('href', '')]
        print(f"Links with /news/: {len(news_links)}")
        
        # Show first few news links
        print("First 10 news links:")
        for i, link in enumerate(news_links[:10], 1):
            href = link.get('href')
            text = link.get_text().strip()[:50]
            print(f"  {i}. {href} -> {text}")
        
        # Check CSS selectors
        print("\nTesting CSS selectors:")
        selectors = [
            'a[href*="/news/"]',
            'a[href*="/business/"]',
            'h1 a', 'h2 a', 'h3 a'
        ]
        
        for selector in selectors:
            matches = soup.select(selector)
            print(f"  {selector}: {len(matches)} matches")
            if matches:
                for i, match in enumerate(matches[:3], 1):
                    href = match.get('href', 'NO_HREF')
                    text = match.get_text().strip()[:30]
                    print(f"    {i}. {href} -> {text}")

if __name__ == "__main__":
    check_html_structure()