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
    name = 'divar_auto'
    allowed_domains = ['divar.ir']

    brands = ['arisun', 'ario', 'alfa-romeo', 'mvm', 'amico', 'opel', 'swm', 'mg', 'iran-khodro', 'baic', 'brilliance',
              'mercedes-benz']
    city_id = "6"
    brand_index = 0

    def start_requests(self):

        brand = self.brands[self.brand_index]
        url = 'https://api.divar.ir/v8/postlist/w/search'

        form_data = {
            "data": {
                "brand_model": {"repeated_string": {"value": [brand]}},
                "category": {"str": {"value": "light"}}
            }
        }

        server_payload = {
            "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
            "additional_form_data": {
                "data": {"sort": {"str": {"value": "sort_date"}}}
            }
        }

        cities = [self.city_id]


        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'Content-Type': 'application/json',
        }

        payload = {
            'form_data_json': json.dumps(form_data),
            'server_payload_json': json.dumps(server_payload),
            'cities': cities
        }

        yield scrapy.Request(
            url=url,
            method="POST",
            headers=headers,
            body=json.dumps(payload),
            callback=self.parse,
            meta={'brand': brand}
        )

    def parse(self, response):
        data = json.loads(response.text)
        brand = response.meta['brand']


        for widget in data.get('list_widgets', []):
            if widget.get('widget_type') == 'POST_ROW':
                car_data = widget.get('data', {})
                title = car_data.get('title', 'N/A')
                price = car_data.get('middle_description_text', 'N/A')
                mileage = car_data.get('top_description_text', 'N/A')
                city = car_data.get('city', 'shiraz')
                image_url = car_data.get('image_url', 'N/A')


                yield {
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                    'city': city,
                    'image_url': image_url,
                }


        if 'last_post_date' in data:
            last_post_date = data['last_post_date']
            url = f'https://api.divar.ir/v8/postlist/w/search?last-post-date={last_post_date}'


            yield scrapy.Request(
                url=url,
                method="POST",
                headers=response.request.headers,
                body=response.request.body,
                callback=self.parse,
                meta={'brand': brand}
            )
        else:

            self.brand_index += 1
            if self.brand_index < len(self.brands):
                yield from self.start_requests()



