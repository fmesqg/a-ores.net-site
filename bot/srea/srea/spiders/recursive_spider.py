import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.url import canonicalize_url

class RecursiveSpider(CrawlSpider):
    name = "recursive_spider"
    allowed_domains = ["srea.azores.gov.pt", "portal.azores.gov.pt"] 
    start_urls = ["https://srea.azores.gov.pt", "https://portal.azores.gov.pt"]

    visited_urls = set()

    # Define the rules for following links within the same domain
    rules = (
        Rule(LinkExtractor(allow=(), unique=True), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # Canonicalize the URL to avoid different representations of the same URL
        canonical_url = canonicalize_url(response.url)

        # Check if the URL has already been visited
        if canonical_url not in self.visited_urls:
            # Add the URL to the visited set
            self.visited_urls.add(canonical_url)
            
            # Yield the URL and continue
            yield {'url': canonical_url}