import scrapy
import json
import time
import tempfile
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule


class DivarCarSpider(scrapy.Spider):
    name = "divar_auto"
    allowed_domains = ["api.divar.ir"]
    start_urls = ['https://api.divar.ir/v8/postlist/w/search']

    def __init__(self, *args, **kwargs):
        super(DivarCarSpider, self).__init__(*args, **kwargs)
        self.brands = [
            "Audi", "Arisan", "Ario", "Alfa Romeo", "Amico", "Opel", "SWM", "SKYWELL", "Smart", "Škoda", "Oldsmobile",
            "MG", "MVM", "Iran Khodro", "Isuzu", "XTRIM", "inroads", "Iveco", "BAIC", "Brilliance", "Besturn",
            "Bestune", "Mercedes-Benz", "Borgward", "BAC", "BMW", "BISU", "BYD", "Buick", "PARS KHODRO", "Pazhan",
            "Pride", "Proton", "Peugeot", "Porsche", "Pontiac", "Paykan", "Tara", "Toyota", "Tiba", "Tigard", "Jetour",
            "JAC", "Jaguar", "Joylong", "JMC", "GAC Gonow", "Jeep", "Geely", "Changan", "Chery", "Datsun", "Domy",
            "Dongfeng", "Dayun", "Daihatsu", "Delica", "Dena", "Dodge", "Daewoo", "DS", "Dignity", "Deer", "Runna",
            "Rayen", "Renault", "Rollsroyce", "Rich", "Respect", "Rigan", "Zamyad", "ZX_AUTO", "Zotye", "SsangYong",
            "Saipa", "Saina", "Seat", "Samand", "Soueast", "Subaru", "Suzuki", "Citroen", "Sinad", "Sinogold", "Shahin",
            "Chevrolet", "Farda", "Foton", "Ford", "Volkswagen", "Fownix", "Fiat", "Fidelity", "Capra", "Chrysler",
            "Quick", "KG Mobility", "Kia", "KMC", "Great-Wall", "Gac", "Qingling", "Lada", "Lamari", "Lamborghini",
            "Lexus", "Land Rover", "Landmark", "Lotus", "LUCANO", "Luxgen", "Lifan", "Maserati", "Mazda", "Maxmotor",
            "Maxus", "Mitsubishi", "MINI", "NETA", "Nissan", "Volvo", "IranKhodro Van", "Faw", "Narvan", "Venucia",
            "VGV", "Hafei Lobo", "Hummer", "Haval", "Haima", "Hanteng", "Honda", "Hongqi", "Hillman", "Hyosow",
            "Hyundai", "Uaz", "other"
        ]
        self.current_brand_index = 0

    def start_requests(self):
        yield self.make_request_for_brand(1, 0)

    def make_request_for_brand(self, page, layer_page, last_post_date=None, search_uid=None):
        if self.current_brand_index >= len(self.brands):
            self.logger.info("All brands processed.")
            return

        brand = self.brands[self.current_brand_index]
        payload = {
            "city_ids": ["6"],
            "pagination_data": {
                "@type": "type.googleapis.com/post_list.PaginationData",
                "last_post_date": last_post_date,
                "layer_page": layer_page,
                "page": page
            },
            "search_uid": search_uid,
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
            "sort": {"str": {"value": "sort_date"}}
        }

        return scrapy.Request(
            url='https://api.divar.ir/v8/postlist/w/search',
            method="POST",
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            callback=self.parse,
            meta={
                'brand': brand,
                'page': page,
                'layer_page': layer_page,
                'last_post_date': last_post_date,
                'search_uid': search_uid
            }
        )

    def parse(self, response):
        brand = response.meta['brand']
        page = response.meta['page']
        layer_page = response.meta['layer_page']
        last_post_date = response.meta['last_post_date']
        search_uid = response.meta['search_uid']

        data = response.json()


        for item in data.get('list_widgets', []):
            if item.get('widget_type') == 'POST_ROW':
                car_data = item['data']
                yield {
                    'brand': brand,
                    'title': car_data.get('title'),
                    'price': car_data.get('middle_description_text', 'N/A'),
                    'mileage': car_data.get('top_description_text', 'N/A'),
                    'location': car_data.get('bottom_description_text', 'N/A'),
                    'image_url': car_data.get('image_url'),
                }


        pagination_data = data.get('pagination', {}).get('data', {})
        new_last_post_date = pagination_data.get('last_post_date')
        has_next_page = data.get('pagination', {}).get('has_next_page')
        new_search_uid = data.get('search_uid', search_uid)

        if has_next_page:
            next_page = page + 1
            yield self.make_request_for_brand(next_page, layer_page, new_last_post_date, new_search_uid)
        else:

            self.current_brand_index += 1
            yield self.make_request_for_brand(1, 0)






class DivarSpider(scrapy.Spider):
    name = "divar"
    allowed_domains = ["api.divar.ir"]
    brand_queue = []

    def start_requests(self):
        url = 'https://api.divar.ir/v8/postlist/w/filters'
        payload = {
            "city_ids": ["6"],
            "data": {
                "form_data": {
                    "data": {
                        "category": {
                            "str": {"value": "light"}
                        }
                    }
                },
                "server_payload": {
                    "@type": "type.googleapis.com/widgets.SearchData.ServerPayload"
                },
                "additional_form_data": {
                    "data": {
                        "sort": {
                            "str": {"value": "sort_date"}
                        }
                    }
                }
            }
        }
        headers = {'Content-Type': 'application/json'}

        yield scrapy.Request(
            url=url,
            method='POST',
            body=json.dumps(payload),
            headers=headers,
            callback=self.parse_brand_names
        )

    def parse_brand_names(self, response):
        data = response.json()
        page = data.get('page', {})
        widget_list = page.get('widget_list', [])

        for widget in widget_list:
            if widget.get('widget_type') == 'EXPANDABLE_FORM_ROW' and widget.get(
                    'uid') == 'filter_brand_model_expandable':
                brand_widget = widget.get('data', {}).get('widget_list', [])
                for brand_data in brand_widget:
                    if brand_data.get('widget_type') == 'I_MULTI_SELECT_HIERARCHY_ROW' and brand_data.get(
                            'uid') == 'filter_brand_model':
                        option_brand = brand_data.get('data', {}).get('options', {})
                        children_brand = option_brand.get('children', [])
                        for child in children_brand:
                            brand_data = child.get('data', {})
                            brand_name = brand_data.get('value', '')
                            if brand_name:
                                self.brand_queue.append(brand_name)

        if self.brand_queue:
            first_brand = self.brand_queue.pop(0)
            yield self.make_request_for_brand(1, 1, first_brand, None, None)
        else:
            self.logger.error("No brands found")

    def make_request_for_brand(self, page, layer_page, brand, last_post_date, search_uid):

        payload = {
            "city_ids": ["6"],
            "pagination_data": {
                "@type": "type.googleapis.com/post_list.PaginationData",
                "last_post_date": last_post_date,
                "layer_page": layer_page,
                "page": page
            },
            "search_uid": search_uid,
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
            "sort": {"str": {"value": "sort_date"}}
        }

        return scrapy.Request(
            url='https://api.divar.ir/v8/postlist/w/search',
            method="POST",
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            callback=self.parse,
            meta={'brand': brand, 'page': page, 'layer_page': layer_page, 'last_post_date': last_post_date, 'search_uid': search_uid}
        )

    def parse(self, response):
        brand = response.meta['brand']
        page = response.meta['page']
        layer_page = response.meta['layer_page']
        last_post_date = response.meta['last_post_date']
        search_uid = response.meta['search_uid']

        data = response.json()
        for item in data.get('list_widgets', []):
            if item.get('widget_type') == 'POST_ROW':
                car_data = item['data']
                title = car_data.get('title')
                price = car_data.get('middle_description_text', 'N/A')
                mileage = car_data.get('top_description_text', 'N/A')
                location = car_data.get('bottom_description_text', 'N/A')
                image_url = car_data.get('image_url')

                yield {
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                    'location': location,
                    'image_url': image_url,
                }

        pagination_data = data.get('pagination', {})
        new_last_post_date = pagination_data.get('data', {}).get('last_post_date')
        has_next_page = pagination_data.get('has_next_page')
        page = pagination_data.get('data', {}).get('page')
        new_search_uid = data.get('search_uid', search_uid)


        if has_next_page:
            next_page = page + 1
            next_layer_page = layer_page + 1
            yield self.make_request_for_brand(next_page, next_layer_page, brand, new_last_post_date, new_search_uid)
        else:
            if self.brand_queue:
                next_brand = self.brand_queue.pop(0)
                yield self.make_request_for_brand(1, 1, next_brand, None,
                                                  None)
            else:
                self.logger.info("All brands processed")


class CarSpider(scrapy.Spider):
    name = 'bama'
    allowed_domains = ['bama.ir']
    start_urls = [
        'https://www.bama.ir/car',
    ]

    def __init__(self, *args, **kwargs):
        super(CarSpider, self).__init__(*args, **kwargs)
        options = Options()
        options.headless = True
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-software-rasterizer')

        profile_dir = tempfile.mkdtemp()
        options.add_argument(f"user-data-dir={profile_dir}")

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def parse(self, response):
        self.driver.get(response.url)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        selector = Selector(text=self.driver.page_source)
        car_links = selector.xpath('//div[@class="bama-adlist-container"]//a/@href').extract()

        for link in car_links:
            time.sleep(2)
            yield response.follow(link, callback=self.parse_car)

        next_page = selector.xpath('//a[@class="next"]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_car(self, response):
        model = response.xpath('normalize-space(//h1[@class="bama-ad-detail-title__title"])').get()
        price = response.xpath(
            'normalize-space(//div[@class="bama-ad-detail-price__section"]//span[@class="bama-ad-detail-price__price-text"])').get()

        yield {
            'model': model,
            'price': price if price else None
        }




class BamaCarSpider(scrapy.Spider):
    name = "bama_cars"
    allowed_domains = ["bama.ir"]
    api_url = "https://bama.ir/cad/api/search?vehicle={brand}&pageIndex={page}"


    brands = ['bmw', 'benz', 'peugeot', 'kia']

    def start_requests(self):
        for brand in self.brands:
            url = self.api_url.format(brand=brand, page=1)
            yield scrapy.Request(url, callback=self.parse, meta={'brand': brand, 'page': 1})


    def parse(self, response):
        data = json.loads(response.body)
        ads = data.get('data', {}).get('ads', [])

        for ad in ads:
            yield {
                'brand': response.meta['brand'],
                'title': ad.get['detail'].get['title'],
                'price': ad['price'].get('price', 'N/A'),
                'year': ad['detail'].get('year', 'N/A'),
                'mileage': ad['detail'].get('mileage', 'N/A'),
                'location': ad['detail'].get('location', 'N/A'),
                'image': ad['detail'].get('image', 'N/A'),
                'color': ad['detail'].get('color', 'N/A'),
            }

        total_pages = data['metadata']['total_pages']
        current_page = response.meta['page']
        if current_page < total_pages:
            next_page = current_page + 1
            next_page_url = self.api_url.format(brand=response.meta['brand'], page=next_page)
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'brand': response.meta['brand'], 'page': next_page})
        else:
            current_brand = response.meta['brand']
            next_brand_index = self.brands.index(current_brand) + 1
            if next_brand_index < len(self.brands):
                next_brand = self.brands[next_brand_index]
                next_brand_url = self.api_url.format(brand=next_brand, page=1)
                yield scrapy.Request(next_brand_url, callback=self.parse, meta={'brand': next_brand, 'page': 1})



# my first crawling
class PricingCarSpider(scrapy.Spider):
    name = 'car_spider'
    allowed_domains = ['www.khodro45.com']
    start_urls = ['https://www.khodro45.com/pricing']


    def parse(self, response):
        for box_pricing in response.css('div.pricing-box'):
            for row in box_pricing.css('div.d-block'):
                model = row.css('div.item__right::text').get()
                price = row.css('span.item__price::text').get()

                if model and price:
                    yield {
                        'model': model.strip(),
                        'price': price.strip(),
                    }
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)



#crawl with using link extractor
class PricingSpider(scrapy.Spider):
    name = 'pricing_spider'
    allowed_domains = ['www.khodro45.com']
    start_urls = ['https://www.khodro45.com/pricing']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="pricing-box"]//a'), callback='parse_pricing', follow=False),
        Rule(LinkExtractor(restrict_xpaths='//a[@class="next"]'), follow=True),
    )


    def parse_pricing(self, response):
        model = response.xpath('//title/text()').get()
        price = response.xpath(
             '//div[@class="d-inline-flex align-items-center justify-content-end flex-wrap"]/div[@class="text-16 font-weight-bold"]/text()').get()
        yield {
            'model': model,
            'price': price
        }


