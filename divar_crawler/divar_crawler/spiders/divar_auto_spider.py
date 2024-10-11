# import time

# import scrapy

# class DivarSpider(scrapy.Spider):
#     name = 'divar_auto'
#     allowed_domains = ['divar.ir']
#     start_urls = ['https://divar.ir/s/shiraz/auto']
#     download_delay = 1
#     page_number = 1

#     def parse(self, response):
#         items = response.xpath('//div[@class="post-list__widget-col-c1444"]')
#         for item in items:
#             time.sleep(2)
#             title = item.xpath('.//h2/text()').get()
#             price = item.xpath('.//div[@class="kt-post-card__description"][2]/text()').get()
#             yield {
#                 'title': title,
#                 'price': price if price else None,
#             }
#         self.page_number += 1
#         next_page = f'https://divar.ir/s/shiraz/auto?page={self.page_number}'
#         yield scrapy.Request(next_page, callback=self.parse)



import scrapy
import json

class DivarSpider(scrapy.Spider):
    name = 'divar_auto'
    allowed_domains = ['divar.ir']

    brands = ['arisun', 'ario', 'alfa-romeo', 'mvm']

    brand_index = 0

    def start_requests(self):
        brand = self.brands[self.brand_index]
        url = f'https://api.divar.ir/v8/web-search/shiraz/car?q={brand}'
        yield scrapy.Request(url=url, callback=self.parse, meta={'brand': brand})

    def parse(self, response):
        data = json.loads(response.text)
        brand =response.meta['brand']

        for car in data.get('list_widgets',[]):
            yield {
                'brand': brand,
                'title': car['data']['title'],
                'price': car['data']['middle_description_text'],
                'milage': car['data']['top_description_text'],
                'city' : car['data']('city', 'shiraz'),
            }

            if 'last_post_date' in data:
                last_post_date = data['last_post_date']
                next_page_url = f'https://api.divar.ir/v8/web-search/shiraz/car?q={brand}&last-post-date={last_post_date}'
                yield scrapy.Request(next_page_url, callback=self.parse, meta={'brand': brand})
            else:
                self.brand_index += 1
                if self.brand_index < len(self.brands):
                    next_brand = self.brands[self.brand_index]
                    next_brand_url = f'https://api.divar.ir/v8/web-search/shiraz/car?q={next_brand}'
                    yield scrapy.Request(next_brand_url, callback=self.parse, meta={'brand': next_brand})