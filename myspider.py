import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

# spiders documentation
# https://docs.scrapy.org/en/latest/topics/spiders.html

# spiders in practice, see below more informations ->
# https://docs.scrapy.org/en/latest/topics/practices.html

# from twisted.internet import reactor
# from scrapy.linkextractors import LinkExtractor

class CoursesSpider(scrapy.Spider):

    name = "edxCourses"
    start_urls = ['https://www.edx.org/course']

    def parse(self, response):
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('*//a/@href').extract()

        for link in all_links:
            yield scrapy.http.Request(url=link, callback=print_this_link)

    def print_this_link(self, link):
        print("Link --> {this_link}".format(this_link=link))

class CourseSpider(scrapy.Spider):
    name = 'edx'
    start_urls = ['https://www.edx.org/course/intro-to-data-science']

    def parse(self, response):
        for description in response.xpath("/html/body//div[contains(@class,'course-description')]"):
            if description.css('p ::text').get().strip():
                yield {'description': description.css('p ::text').get()}

        for category in response.xpath("/html/body//a[contains(@href,'subject')]"):
            if category.css('a ::text').get().strip():
                yield {'category': category.css('a ::text').get()}

        # for next_page in response.css('a.next-posts-link'):
        #     yield response.follow(next_page, self.parse)

configure_logging()
runner = CrawlerRunner()
runner.crawl(CoursesSpider)
runner.start()