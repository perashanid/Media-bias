#!/usr/bin/env python3
"""
Check encoding issues with news sites
"""

import requests
from bs4 import BeautifulSoup

def check_site_encoding(url, site_name):
    """Check encoding and HTML parsing"""
    print(f"\n{'='*20} {site_name} {'='*20}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        print(f"Encoding from headers: {response.encoding}")
        
        # Try different parsing approaches
        print("\n--- Parsing with default encoding ---")
        soup1 = BeautifulSoup(response.content, 'html.parser')
        links1 = soup1.find_all('a', href=True)
        print(f"Links found: {len(links1)}")
        
        print("\n--- Parsing with UTF-8 ---")
        soup2 = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        links2 = soup2.find_all('a', href=True)
        print(f"Links found: {len(links2)}")
        
        # Show some raw HTML
        print("\n--- Raw HTML sample (first 500 chars) ---")
        print(response.text[:500])
        
        # Show parsed HTML sample
        if links1:
            print("\n--- First 5 parsed links ---")
            for i, link in enumerate(links1[:5], 1):
                href = link.get('href', '')
                text = link.get_text().strip()[:30]
                print(f"  {i}. {href} -> {text}")
        elif links2:
            print("\n--- First 5 parsed links (UTF-8) ---")
            for i, link in enumerate(links2[:5], 1):
                href = link.get('href', '')
                text = link.get_text().strip()[:30]
                print(f"  {i}. {href} -> {text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_site_encoding("https://www.thedailystar.net", "The Daily Star")