#!/usr/bin/env python3
"""
Check actual HTML content from news sites
"""

import requests
from bs4 import BeautifulSoup

def check_site_html(url, site_name):
    """Check HTML content of a site"""
    print(f"\n{'='*20} {site_name} {'='*20}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for links
        all_links = soup.find_all('a', href=True)
        print(f"Total links: {len(all_links)}")
        
        # Show first few links
        print("First 10 links:")
        for i, link in enumerate(all_links[:10], 1):
            href = link.get('href', '')
            text = link.get_text().strip()[:50]
            print(f"  {i}. {href} -> {text}")
        
        # Check for common article patterns
        article_links = []
        for link in all_links:
            href = link.get('href', '')
            if any(pattern in href for pattern in ['/news/', '/article/', '/story/', '/post/', '/details/']):
                article_links.append(href)
        
        print(f"Potential article links: {len(article_links)}")
        for i, link in enumerate(article_links[:5], 1):
            print(f"  {i}. {link}")
            
        # Check page title
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sites = [
        ("https://www.thedailystar.net", "The Daily Star"),
        ("https://www.prothomalo.com", "Prothom Alo"),
        ("https://www.bd-pratidin.com", "BD Pratidin"),
        ("https://www.atnnewstv.com", "ATN News"),
    ]
    
    for url, name in sites:
        check_site_html(url, name)