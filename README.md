Overview

This project is a web crawler built using Scrapy and Selenium. The crawler is designed to extract data from websites that require dynamic content rendering (JavaScript-heavy pages), combining the efficiency of Scrapy for static content scraping and the flexibility of Selenium for JavaScript execution.
Table of Contents

    . Prerequisites
    . Installation
    . Project Structure
    . Configuration
    . Usage
    . Custom Settings
    . Contributing
    . License

Prerequisites

Ensure you have the following installed:

        Python 3.8+
        Pip (Python package manager)
        Google Chrome or Firefox browser (depending on your Selenium driver choice)
        ChromeDriver or GeckoDriver for Selenium, depending on your browser
            ChromeDriver #for using Chrome
            GeckoDriver  #for using Firefox

Installation

Clone the repository:

    bash

        git clone https://github.com/Alirezaalireza77/crawler.git
        cd divar_crawler

Install dependencies:

bash

        pip install -r requirements.txt

        Install the appropriate browser driver (e.g., ChromeDriver or GeckoDriver) and ensure it's in your system's PATH.

Project Structure

bash

crawler-project/
│
├── crawler/
│   ├── spiders/              # Spider definitions
│   │   └── example_spider.py
│   ├── middlewares.py        # Custom middlewares including Selenium integration
│   ├── settings.py           # Scrapy project settings
│   └── items.py              # Item structure for scraped data
│
├── logs/                     # Directory for logging information
│
├── requirements.txt          # Required packages (Scrapy, Selenium, etc.)
├── README.md                 # This README file
└── run_crawler.py            # Main script to run the crawler

Configuration
Scrapy Settings

All Scrapy settings, including custom configurations for Selenium, can be found in crawler/settings.py. The key settings include:

        BOT_NAME: Name of the bot.
        SPIDER_MODULES: Path to your spider modules.
        ROBOTSTXT_OBEY: Set to True or False to follow or ignore robots.txt.
        SELENIUM_DRIVER_NAME: Set to 'chrome', 'firefox', or another browser that Selenium supports.
        SELENIUM_DRIVER_EXECUTABLE_PATH: Path to your chromedriver or geckodriver.
        SELENIUM_DRIVER_ARGUMENTS: Arguments passed to the Selenium WebDriver.

Example Selenium integration configuration in settings.py:

python

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = '/path/to/chromedriver'
SELENIUM_DRIVER_ARGUMENTS=['--headless']  # '--headless' for running without UI

Selenium Middleware

The crawler uses a custom Selenium middleware, which you can configure or modify in crawler/middlewares.py. This middleware intercepts requests for pages requiring JavaScript execution and uses Selenium to render them before passing the content to Scrapy.
Usage
Running the Spider

To run the spider, use the following command:

bash

    scrapy crawl example_spider

Running with Selenium

If your website requires dynamic content rendering, the Selenium middleware will automatically take over for those requests. Ensure that your spider handles both static and dynamic pages appropriately.
Custom Spider Example

Here’s an example of how to create a new spider:

python

import scrapy
from scrapy_selenium import SeleniumRequest

class ExampleSpider(scrapy.Spider):
    name = 'example_spider'
    
    def start_requests(self):
        urls = ['https://example.com/']
        for url in urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        title = response.css('title::text').get()
        yield {
            'title': title,
            'url': response.url
        }

Custom Settings

You can adjust custom settings in settings.py depending on the website you're scraping, such as:

    DOWNLOAD_DELAY: Adjust to avoid being flagged for scraping too quickly.
    CONCURRENT_REQUESTS: Number of concurrent requests Scrapy should process.
    RETRY_TIMES: The number of times a request will be retried in case of failures.

Logs

Logs will be stored in the logs/ directory. You can customize logging levels in settings.py:

python

LOG_LEVEL = 'INFO'  # Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'logs/crawler.log'



    Fork the repository.
    Create a feature branch: git checkout -b new-feature.
    Commit your changes: git commit -m 'Add new feature'.
    Push to the branch: git push origin new-feature.
    Open a pull request.



This project is licensed under the MIT License - see the LICENSE file for details.

Enjoy crawling! If you encounter any issues, feel free to open an issue or contribute to the project.

Alireza
github : Alirezaalireza77
