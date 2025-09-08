"""
Configuration for the web crawler
Change these settings to customize how the crawler works
"""

# Websites to start crawling from
SEED_URLS = [
    "https://example.com",
    "https://httpbin.org/html",
]

# How many pages to crawl maximum
MAX_PAGES = 50

# How long to wait between requests (seconds)
# This is polite - don't overload websites!
DELAY_BETWEEN_REQUESTS = 1

# What to call our crawler (websites can see this)
USER_AGENT = "SimpleWebCrawler/1.0"

# Files to save results
PAGES_FILE = "crawled_pages.txt"
LINKS_FILE = "found_links.txt"

# Skip these file types
SKIP_EXTENSIONS = ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']