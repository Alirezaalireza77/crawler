import scrapy
class DivarAutoSpider(scrapy.Spider):
    name = 'divar_auto'
    start_urls = ['https://divar.ir/s/shiraz/auto']

    def parse(self, response):
        for post in response.xpath('//article[contains(@class, "kt-post-card")]'):
            model = post.xpath('.//h2[@class="kt-post-card__title"]/text()').get()
            price = post.xpath('.//div[contains(@class, "kt-post-card__description")][2]/text()').get()

            yield {
                'model': model,
                'price': price,
            }
        next_page = response.xpath('//a[@class="pagination__next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

