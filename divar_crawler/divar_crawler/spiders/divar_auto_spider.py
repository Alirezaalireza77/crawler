# import time
#
# import scrapy
#
# class DivarSpider(scrapy.Spider):
#     name = 'divar_auto'
#     allowed_domains = ['divar.ir']
#     start_urls = ['https://divar.ir/s/shiraz/auto']
#     download_delay = 1
#     page_number = 1
#
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


class DivarCarSpider(scrapy.Spider):
    name = "divar_auto"
    allowed_domains = ["api.divar.ir"]
    start_urls = ['https://api.divar.ir/v8/postlist/w/search']


    brands = ['arisun', 'ario', 'alfa-romeo', 'mvm', 'amico', 'opel', 'swm', 'mg',
              'iran-khodro', 'baic', 'brilliance', 'mercedes-benz', 'saipa']


    brand_index = 0

    def start_requests(self):

        if self.brand_index < len(self.brands):
            brand = self.brands[self.brand_index]
            yield self.make_request_for_brand(brand, 1)

    def make_request_for_brand(self, brand, page):

        payload = {
            "city_ids": ["6"],
            "search_data": {
                "form_data": {
                    "data": {
                        "brand_model": {
                            "repeated_string": {"value": [brand]}
                        },
                        "category": {
                            "str": {"value": "light"}
                        }
                    }
                }
            },
            "sort": {"str": {"value": "sort_date"}},
            "page": page
        }
        return scrapy.Request(
            url='https://api.divar.ir/v8/postlist/w/search',
            method="POST",
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            callback=self.parse,
            meta={'brand': brand, 'page': page}
        )

    def parse(self, response):
        data = response.json()
        brand = response.meta['brand']
        page = response.meta['page']


        for item in data.get('list_widgets', []):
            if item.get('widget_type') == 'POST_ROW':
                car_data = item['data']
                title = car_data.get('title')
                price = car_data.get('middle_description_text', 'N/A')

                yield {
                    'brand': brand,
                    'title': title,
                    'price': price,
                }


        if data.get('pagination', {}).get('has_next_page'):
            next_page = page + 1

            yield self.make_request_for_brand(brand, next_page)
        else:

            self.brand_index += 1
            if self.brand_index < len(self.brands):
                next_brand = self.brands[self.brand_index]
                yield self.make_request_for_brand(next_brand, 1)
