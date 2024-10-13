import scrapy
import json
import time
import tempfile
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class DivarCarSpider(scrapy.Spider):
    name = "divar_auto"
    allowed_domains = ["api.divar.ir"]
    start_urls = ['https://api.divar.ir/v8/postlist/w/search']


    def __init__(self, *args, **kwargs):
        super(DivarCarSpider, self).__init__(*args, **kwargs)
        self.brands = ["Audi","Arisan","Ario","Alfa Romeo","Amico","Opel","SWM","SKYWELL","Smart","Škoda","Oldsmobile",
                       "MG","MVM","Iran Khodro","Isuzu","XTRIM","inroads","Iveco","BAIC","Brilliance","Besturn","Bestune",
                       "Mercedes-Benz","Borgward","BAC","BMW","BISU","BYD","Buick","PARS KHODRO","Pazhan","Pride","Proton",
                       "Peugeot","Porsche","Pontiac","Paykan","Tara","Toyota","Tiba","Tigard","Jetour","JAC","Jaguar",
                       "Joylong","JMC","GAC Gonow","Jeep","Geely","Changan","Chery","Datsun","Domy","Dongfeng","Dayun",
                       "Daihatsu","Delica","Dena","Dodge","Daewoo","DS","Dignity","Deer","Runna","Rayen","Renault","Rollsroyce",
                       "Rich","Respect","Rigan","Zamyad","ZX_AUTO","Zotye","SsangYong","Saipa","Saina","Seat","Samand","Soueast",
                       "Subaru","Suzuki","Citroen","Sinad","Sinogold","Shahin","Chevrolet","Farda","Foton","Ford","Volkswagen",
                       "Fownix","Fiat","Fidelity","Capra","Chrysler","Quick","KG Mobility","Kia","KMC","Great-Wall","Gac",
                       "Qingling","Lada","Lamari","Lamborghini","Lexus","Land Rover","Landmark","Lotus","LUCANO","Luxgen",
                       "Lifan","Maserati","Mazda","Maxmotor","Maxus","Mitsubishi","MINI","NETA","Nissan","Volvo","IranKhodro Van",
                       "Faw","Narvan","Venucia","VGV","Hafei Lobo","Hummer","Haval","Haima","Hanteng","Honda","Hongqi","Hillman",
                       "Hyosow","Hyundai","Uaz","other",
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
                yield self.make_request_for_brand(1, next_brand_index)



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
