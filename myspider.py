import scrapy

class BlogSpider(scrapy.Spider):
    name = 'edx'
    start_urls = ['https://www.edx.org/course/intro-to-data-science']

    def parse(self, response):
        for description in response.xpath('//*[@id="main-content"]/section/div/div/div/div[2]/div[1]/div/div[2]/div'):
            yield {'description': description.css('p ::text').get()}
        for category in response.xpath('//*[@id="main-content"]/section/div/div/div/div[1]/div/div[1]/ul/li[5]/div[2]/a'):
             yield {'category': category.get()}

        # for next_page in response.css('a.next-posts-link'):
        #     yield response.follow(next_page, self.parse)
