# -*- coding: utf-8 -*-
#from scrapy.settings.default_settings import FEED_FORMAT, FEED_URI
import logging
import sys
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
# Scrapy settings for SkuScraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'BMC-CRAWLER'

SPIDER_MODULES = ['SkuScraper.spiders']
NEWSPIDER_MODULE = 'SkuScraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'SkuScraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
 }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'SkuScraper.middlewares.MyCustomDownloaderMiddleware': 543,
# }

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'SkuScraper.pipelines.MongoPipeline': 300,
    
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = False
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 200
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'



DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
#DOWNLOAD_FAIL_ON_DATALOSS = False
RETRY_TIMES = 0


REACTOR_THREADPOOL_MAXSIZE = 50
#DOWNLOAD_TIMEOUT = 360
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 404]



# Memory #

MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1900
MEMUSAGE_CHECK_INTERVAL_SECONDS = 30
MEMUSAGE_NOTIFY_MAIL = ['user@mail.com']

DUPEFILTER_DEBUG = True


# Slash Settings #
SPLASH_URL = 'http://127.0.0.1:8050/'
HTTP_USER = 'user'
HTTP_PASSWORD = 'userpass'

# Mongo Settings #
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "bmc_skus"
MONGODB_COLLECTION = "ecom_skus"

MONGO_URI = "mongodb://admin:password@127.0.0.1:27017/bmc_skus"
#MONGO_URI = "mongodb://localhost:27017/products"
MONGO_DATABASE = "bmc_skus"

TEST_DOMAIN_NAME = 'http://www.google.com/'


# Provide AMQP connection string
RABBITMQ_CONNECTION_PARAMETERS = 'amqp://admin:password@127.0.0.1:5672/'
RABBITMQ_USER = 'admin'
RABBITMQ_PASSWORD = 'password'
RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_SOCKET_TIMEOUT = 300


# Provide AMQP connection string
SFTP_USER = 'user'
SFTP_PASSWORD = ''
SFTP_HOST = '127.0.0.1'
SFTP_FILE_PATH = '/home/users/test/scraped_skus/'


DIVISION_Q = 'divisions'
CATEGORY_Q = 'categories'
CATEGORY_ERROR_Q = 'categories_error'
PRODUCTS_Q = 'products'
FILTERED_PRODUCTS_Q = 'filtered_products'
OUT_OF_STOCK_PRODUCTS_Q = 'out_of_stock_products'



# Export Feed settings#

#FEED_FORMAT = "csv"
#FEED_URI = "skus.csv"
#FEED_EXPORT_FIELDS = ["skuList"]


GAP_SKIP_DIVISIONS = ['gap factory']





#
PRODUCT_COUNT_PER_PAGE = 300


#### Spider Custom Settings #####




BASE_SPIDER_CUSTOM_SETTINGS = {
        'ITEM_PIPELINES' : {
    
        }
    }

DIVISION_SPIDER_CUSTOM_SETTINGS = {'CONCURRENT_REQUESTS' : 10,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10, 
        'DOWNLOAD_DELAY' : 1,
        'RETRY_TIMES' : 3}

CATEGORY_SPIDER_CUSTOM_SETTINGS = {
        'CONCURRENT_REQUESTS' : 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2, 
        'DOWNLOAD_DELAY' : 2,
        'RETRY_TIMES' : 2
    }

PRODUCT_SPIDER_CUSTOM_SETTINGS = {
        'CONCURRENT_REQUESTS' : 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'DOWNLOAD_DELAY' : 1,
        'AUTOTHROTTLE_ENABLED' : True,
        'AUTOTHROTTLE_START_DELAY' : 5,
        'AUTOTHROTTLE_MAX_DELAY' : 30,
        'AUTOTHROTTLE_TARGET_CONCURRENCY' : 200,
        'REDIRECT_ENABLED' : True
    }

PRODUCT_SCRAPER_CUSTOM_SETTINGS = {
        'CONCURRENT_REQUESTS' : 500,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 500, 
        'DOWNLOAD_DELAY' : 0.01,
    }        


'''
REMOTE_FILE_SERVER = '10.10.10.10'
REMOTE_FILE_PATH = ''
REMOTE_FILE_NAME = 'unique_skus'
'''


# Logging #
configure_logging(install_root_handler=False)
logging.basicConfig(
        filename='bmc_crawler_log.txt',
        format='[%(asctime)s] [%(levelname)s] : %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO
    )
logging.getLogger("pika").setLevel(logging.WARNING)

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] : %(message)s','%m/%d/%Y %I:%M:%S %p')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

logging.debug('debug')
logging.info('info')
logging.warning('warning')
logging.error('error')
logging.exception('exp')


