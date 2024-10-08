# import scrapy
# import time
# import tempfile
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
#
#
# class DivarSpider(scrapy.Spider):
#     name = 'divar_auto'
#     allowed_domains = ['divar.ir']
#     start_urls = [
#         'https://www.divar.ir/s/shiraz/auto',
#     ]
#
#     def __init__(self, *args, **kwargs):
#         super(DivarSpider, self).__init__(*args, **kwargs)
#         options = Options()
#         options.headless = True
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-gpu')
#         options.add_argument('--remote-debugging-port=9222')
#         profile_dir = tempfile.mkdtemp()
#         options.add_argument(f"user-data-dir={profile_dir}")
#
#         self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#
#     def parse(self, response):
#         self.driver.get(response.url)
#         car_links = response.xpath('//div[contains(@class, "post-list__widget-col-c1444")]//a[@class="kt-post-card__action"]/@href').extract()
#         for link in car_links:
#             yield response.follow(link, callback=self.parse_car)
#         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         next_page = response.xpath('//a[@class="kt-pagination__link kt-pagination__link--next"]/@href').get()
#         if next_page:
#             yield response.follow(next_page, callback=self.parse)
#
#     def parse_car(self, response):
#
#         # model = response.xpath("//h1[contains(@class, 'kt-page-title__title')]/text()").get()
#         model = response.xpath("//title/text()").get()
#         price = response.xpath("//div[contains(@class, 'kt-base-row') and contains(., 'قیمت پایه')]//p[contains(@class, 'kt-unexpandable-row__value')]/text()").get()
#
#         if model and price:
#             yield {
#                 'model': model,
#                 'price': price if price else None,
#             }
#
#     def __del__(self):
#         if hasattr(self, 'driver'):
#             self.driver.quit()



import scrapy

class DivarSpider(scrapy.Spider):
    name = 'divar_auto'
    allowed_domains = ['divar.ir']
    start_urls = ['https://divar.ir/s/shiraz/auto?page=2']
    download_delay = 1  # Introduce a 1-second delay

    def parse(self, response):
        for item in response.xpath('//div[@class="post-list__widget-col-c1444"]'):
            title = item.xpath('.//h2/text()').get()
            price = item.xpath('.//div[@class="kt-post-card__description"][2]/text()').get()

            yield {
                'title': title,
                'price': price,
            }

        next_page = response.xpath('//a[@class="next-page"]/@href').get()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)