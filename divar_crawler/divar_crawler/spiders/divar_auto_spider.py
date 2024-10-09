import time

import scrapy

class DivarSpider(scrapy.Spider):
    name = 'divar_auto'
    allowed_domains = ['divar.ir']
    start_urls = ['https://divar.ir/s/shiraz/auto']
    download_delay = 1
    page_number = 1

    def parse(self, response):
        items = response.xpath('//div[@class="post-list__widget-col-c1444"]')
        for item in items:
            time.sleep(2)
            title = item.xpath('.//h2/text()').get()
            price = item.xpath('.//div[@class="kt-post-card__description"][2]/text()').get()
            yield {
                'title': title,
                'price': price if price else None,
            }
        self.page_number += 1
        next_page = f'https://divar.ir/s/shiraz/auto?page={self.page_number}'
        yield scrapy.Request(next_page, callback=self.parse)
