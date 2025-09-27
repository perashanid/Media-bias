#!/usr/bin/env python3
"""
Investigate ATN News daily sitemaps for actual article URLs
"""

import requests
from bs4 import BeautifulSoup

def investigate_daily_sitemap():
    """Get actual article URLs from ATN News daily sitemap"""
    print("=== ATN News Daily Sitemap Investigation ===")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Get today's sitemap
        daily_sitemap_url = "https://www.atnnewstv.com/sitemap/sitemap-daily-2025-09-28.xml"
        response = requests.get(daily_sitemap_url, headers=headers, timeout=30)
        print(f"Daily sitemap status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            
            # Get all article URLs
            urls = soup.find_all('loc')
            print(f"Articles in today's sitemap: {len(urls)}")
            
            article_urls = []
            for url_elem in urls:
                url = url_elem.get_text()
                article_urls.append(url)
            
            # Show sample URLs
            print("\nSample article URLs:")
            for url in article_urls[:10]:
                print(f"  - {url}")
            
            # Test one actual article
            if article_urls:
                test_url = article_urls[0]
                print(f"\n--- Testing Actual Article: {test_url} ---")
                
                try:
                    article_response = requests.get(test_url, headers=headers, timeout=30)
                    print(f"Article status: {article_response.status_code}")
                    
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        
                        # Test title
                        title_selectors = ['h1', 'title', '.title', '.headline']
                        for selector in title_selectors:
                            title_elem = article_soup.select_one(selector)
                            if title_elem and title_elem.get_text().strip():
                                print(f"Title ({selector}): {title_elem.get_text().strip()[:100]}...")
                                break
                        
                        # Test content selectors
                        content_selectors = [
                            '.content', '.article-content', '.news-content', 
                            '.story-content', 'article', '.post-content',
                            '.entry-content', '.news-body', '.article-body'
                        ]
                        
                        for selector in content_selectors:
                            content_elem = article_soup.select_one(selector)
                            if content_elem:
                                content_text = content_elem.get_text().strip()
                                if len(content_text) > 100:
                                    print(f"Content found with '{selector}': {len(content_text)} chars")
                                    print(f"Preview: {content_text[:200]}...")
                                    break
                        
                        # Look for author
                        author_selectors = ['.author', '.byline', '.writer', '.reporter']
                        for selector in author_selectors:
                            author_elem = article_soup.select_one(selector)
                            if author_elem and author_elem.get_text().strip():
                                print(f"Author ({selector}): {author_elem.get_text().strip()}")
                                break
                        
                        # Look for date
                        date_selectors = ['time', '.date', '.publish-date', '.published']
                        for selector in date_selectors:
                            date_elem = article_soup.select_one(selector)
                            if date_elem:
                                date_text = date_elem.get('datetime') or date_elem.get_text().strip()
                                if date_text:
                                    print(f"Date ({selector}): {date_text}")
                                    break
                        
                except Exception as e:
                    print(f"Error testing article: {e}")
            
            return article_urls
            
    except Exception as e:
        print(f"Daily sitemap error: {e}")
        return []

def main():
    """Main investigation"""
    article_urls = investigate_daily_sitemap()
    print(f"\nFound {len(article_urls)} article URLs from ATN News daily sitemap")

if __name__ == "__main__":
    main()