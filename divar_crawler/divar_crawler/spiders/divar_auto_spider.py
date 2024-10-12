import scrapy
import json
class DivarCarSpider(scrapy.Spider):
    name = "divar_auto"
    allowed_domains = ["api.divar.ir"]
    start_urls = ['https://api.divar.ir/v8/postlist/w/search']
    brands = ['arisun', 'ario', 'alfa-romeo', 'mvm', 'amico', 'opel', 'swm', 'mg',
              'iran-khodro', 'baic', 'brilliance', 'mercedes-benz', 'saipa', 'besturn',
              'bmw', 'pars-khodro', 'peugeot', 'porsche', 'tara', 'renault', 'toyota',
              'tiba', 'tigard', 'jac', 'jeep', 'dena', 'geely', 'dongfeng', 'chery',
              'audi', 'respect', 'runna', 'ssangyong', 'saina', 'samand', 'ford',
              'fownix']

    brand_index = 0

    def start_requests(self):
            brand = self.brands[self.brand_index]
            yield self.make_request_for_brand(brand, 1)

    def make_request_for_brand(self, brand, page):
                payload = {
                    "city_ids": ["6"],
                    "search_data": {
                        "form_data": {
                            "data": {
                                "brand_model": {
                                    "repeated_string": {
                                        "value": [brand]}
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
                    meta={'value': brand, 'page': page}
                )

    def parse(self, response):
        data = response.json()
        brand = response.meta['value']
        page = response.meta['page']

        for item in data.get('list_widgets', []):
            if item.get('widget_type') == 'POST_ROW':
                car_data = item['data']
                title = car_data.get('title')
                price = car_data.get('middle_description_text', 'N/A')
                milage = car_data.get('top_description_text', 'N/A')
                yield {
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'milage': milage,
                    }

        if data.get('pagination', {}).get('has_next_page'):
            next_page = page + 1
            yield self.make_request_for_brand(brand, next_page)
        self.brand_index += 1
        if self.brand_index < len(self.brands):
            next_brand = self.brands[self.brand_index]
            yield self.make_request_for_brand(next_brand, 1)




