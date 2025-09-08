"""
Simple Web Crawler
A beginner-friendly web crawler that visits web pages and extracts content
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import config


class SimpleCrawler:
    def __init__(self):
        # Keep track of what we've already visited
        self.visited_urls = set()
        self.found_links = []
        self.crawled_pages = []
        
        # Setup for web requests
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    def is_valid_url(self, url):
        """Check if URL is worth crawling"""
        try:
            parsed = urlparse(url)
            
            # Must be http or https
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Skip files we don't want
            for ext in config.SKIP_EXTENSIONS:
                if parsed.path.lower().endswith(ext):
                    return False
            
            return True
        except:
            return False
    
    def get_page_content(self, url):
        """Download a web page"""
        try:
            print(f"Crawling: {url}")
            
            response = self.session.get(url, timeout=10)
            
            # Only process successful responses
            if response.status_code == 200:
                return response.text
            else:
                print(f"  Error: Got status code {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  Error downloading {url}: {e}")
            return None
    
    def extract_content_and_links(self, html, base_url):
        """Extract text and links from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Get page title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get main text content
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
            # Find all links
            links = []
            for link in soup.find_all('a', href=True):
                # Make relative URLs absolute
                absolute_url = urljoin(base_url, link['href'])
                if self.is_valid_url(absolute_url):
                    links.append(absolute_url)
            
            return title_text, text, links
            
        except Exception as e:
            print(f"  Error parsing HTML: {e}")
            return "Error", "", []
    
    def save_page(self, url, title, content):
        """Save page content to file"""
        page_info = f"\n{'='*50}\nURL: {url}\nTitle: {title}\n{'='*50}\n{content}\n"
        self.crawled_pages.append(page_info)
    
    def save_links(self, links):
        """Save found links to list"""
        self.found_links.extend(links)
    
    def crawl(self):
        """Main crawling function"""
        print("Starting web crawler...")
        print(f"Will crawl up to {config.MAX_PAGES} pages")
        
        # Start with seed URLs
        urls_to_visit = config.SEED_URLS.copy()
        pages_crawled = 0
        
        while urls_to_visit and pages_crawled < config.MAX_PAGES:
            # Get next URL to visit
            current_url = urls_to_visit.pop(0)
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Download the page
            html_content = self.get_page_content(current_url)
            if html_content is None:
                continue
            
            # Extract content and links
            title, text, links = self.extract_content_and_links(html_content, current_url)
            
            # Save the page
            self.save_page(current_url, title, text)
            self.save_links(links)
            
            # Add new links to visit (limit to avoid too many)
            new_links = [link for link in links[:5] if link not in self.visited_urls]
            urls_to_visit.extend(new_links)
            
            pages_crawled += 1
            print(f"  Crawled page {pages_crawled}/{config.MAX_PAGES}")
            print(f"  Found {len(links)} links")
            
            # Be polite - wait between requests
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
        
        print(f"\nCrawling finished! Visited {pages_crawled} pages")
        self.save_results()
    
    def save_results(self):
        """Save all results to files"""
        # Save crawled pages
        with open(config.PAGES_FILE, 'w', encoding='utf-8') as f:
            f.write("WEB CRAWLER RESULTS\n")
            f.write(f"Crawled {len(self.crawled_pages)} pages\n")
            for page in self.crawled_pages:
                f.write(page)
        
        # Save found links
        with open(config.LINKS_FILE, 'w', encoding='utf-8') as f:
            f.write("FOUND LINKS\n")
            f.write(f"Total: {len(self.found_links)} links\n\n")
            for link in sorted(set(self.found_links)):  # Remove duplicates and sort
                f.write(f"{link}\n")
        
        print(f"Results saved to {config.PAGES_FILE} and {config.LINKS_FILE}")