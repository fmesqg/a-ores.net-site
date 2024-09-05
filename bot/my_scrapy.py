from urllib.parse import urlparse

import scrapy


class DomainSpider(scrapy.Spider):
    name = "domain_spider"
    start_urls = ["https://srea.azores.gov.pt/"]  # Starting point for the spider

    def parse(self, response):
        domain = urlparse(response.url).netloc

        # Extract all links from the page
        for a_tag in response.css("a::attr(href)"):
            link = a_tag.get()
            # Convert relative URLs to absolute
            link = response.urljoin(link)
            # Only follow links from the same domain
            if urlparse(link).netloc == domain:
                yield {"url": link}
            if link is not None:
                response.follow(link, self.parse)


# Run this spider by saving the script to a file and running:
# scrapy runspider <script_name.py>
