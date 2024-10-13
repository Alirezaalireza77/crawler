import scrapy
import json


class DivarCarSpider(scrapy.Spider):
    name = "divar_auto"
    allowed_domains = ["api.divar.ir"]
    start_urls = ['https://api.divar.ir/v8/postlist/w/search']


    def __init__(self, *args, **kwargs):
        super(DivarCarSpider, self).__init__(*args, **kwargs)
        self.brands = [
            'arisun', 'ario', 'alfa-romeo', 'mvm', 'amico', 'opel', 'swm', 'mg',
            'iran-khodro', 'baic', 'brilliance', 'mercedes-benz', 'saipa', 'besturn',
            'bmw', 'pars-khodro', 'peugeot', 'porsche', 'tara', 'renault', 'toyota',
            'tiba', 'tigard', 'jac', 'jeep', 'dena', 'geely', 'dongfeng', 'chery',
            'audi', 'respect', 'runna', 'ssangyong', 'saina', 'samand', 'ford',
            'fownix', 'byd'
        ]


    def start_requests(self):
        yield self.make_request_for_brand(1, 0)


    def make_request_for_brand(self, page, brand_index):
        brand = self.brands[brand_index]
        payload = {
            "city_ids": ["6"],
            "search_data": {
                "form_data": {
                    "data": {
                        "brand_model": {
                            "repeated_string": {
                                "value": [brand]
                            }
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
            meta={'brand': brand, 'page': page, 'brand_index': brand_index}
        )


    def parse(self, response):
        brand = response.meta['brand']
        page = response.meta['page']
        brand_index = response.meta['brand_index']

        data = response.json()

        for item in data.get('list_widgets', []):
            if item.get('widget_type') == 'POST_ROW':
                car_data = item['data']
                title = car_data.get('title')
                price = car_data.get('middle_description_text', 'N/A')
                mileage = car_data.get('top_description_text', 'N/A')


                yield {
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                }

        if data.get('pagination', {}).get('has_next_page'):
            next_page = page + 1
            yield self.make_request_for_brand(next_page, brand_index)
        else:
            next_brand_index = brand_index + 1
            if next_brand_index < len(self.brands):
                yield self.make_request_for_brand(1, next_brand_index)  # Start from page 1 of the next brand

