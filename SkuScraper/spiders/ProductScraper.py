
import json
import re
import scrapy
from scrapy_splash import SplashRequest
from SkuScraper.items import SkuscraperItem
import logging
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
from scrapy.settings import Settings
import pika
from scrapy.contrib.spiders import CrawlSpider
from time import time
from SkuScraper.common import Constants
from SkuScraper.common.utils.mq.RabbitMQUtil import RabbitMQUtil
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
from SkuScraper.common.utils.XpathUtil import XpathUtil
from SkuScraper.common.utils.LuaUtil import LuaUtil
   
class ProductScraper(CrawlSpider):
    name =  Constants.PRODUCT_SCRAPER_NAME
    settings = Settings(get_project_settings())
    http_user = settings.get(Constants.HTTP_USER, None)
    http_pass = settings.get(Constants.HTTP_PASSWORD, None)
    custom_settings = settings.get(Constants.PRODUCT_SCRAPER_CUSTOM_SETTINGS, None)
    
       
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ProductScraper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        logging.info("Scraping spider opened!###!!!!!!!!!!!!!!!!!!")
        if self.queue_purge_flag :
            RabbitMQUtil.purge_queue(self.channel, self.out_of_stock_products_queue);# Purge all outbound queues
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = False

    
    def spider_closed(self, spider):
        logging.info("Scraping spider closed!###!!!!!!!!!!!!!!!!!!")
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, True)
        if q_len !=0 :
            self.runner.crawl(ProductScraper,spider_params=self.spider_params)
            self.runner.join()
        else :
            self.closeConnections()
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = True
            
        
    def __init__(self, *args, **kwargs):
        super(ProductScraper, self).__init__(*args, **kwargs)
        self.spider_params = kwargs.get(Constants.SPIDER_PARAMS)
        self.initializeBaseProperties(self.spider_params)
        self.initializeMongoDB()
        self.initializeRabbitMQ() 
        
        
    def start_requests(self):
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
        while q_len !=0 :
            method_frame, header_frame, body = self.channel.basic_get(
                          queue=self.inbound_queue,
                          no_ack=False) 
            url = body.decode()
            div_name = header_frame.headers.get('div_name')
            cat_name = header_frame.headers.get('cat_name')
            delivery_tag = method_frame.delivery_tag
            logging.info(" [x] Received product %r" % url)
            q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
            yield scrapy.Request(str(url), self.extractSkusForStyle,errback=self.handle_error,dont_filter=True, meta={'delivery_tag': delivery_tag, 'div_name':div_name,'cat_name': cat_name, 'url': str(url)})


    def generateItem(self, url, pattern, scripts):
        isProductDataLoaded = False
        item = SkuscraperItem()
        for script in scripts:
            ss = script.prettify()
            if (pattern.search(ss)):
                isProductDataLoaded = True
                productData = pattern.search(script.string)
                productJson = json.loads("{" + productData.groups()[0] + "}")
                item['brand'] = self.brand
                item['name'] = productJson["name"]
                item['styleId'] = productJson["styleId"]
                item['categoryId'] = productJson["categoryId"]
                item['url'] = url
                item['skuList'] = []
                variants = productJson["variants"]
                for variant in variants:
                    if ("productStyleColors" in variant and variant["productStyleColors"] is not None):
                        productStyleColorsList = variant["productStyleColors"]
                        for productStyleColors in productStyleColorsList:
                            for productStyleColor in productStyleColors:
                                sizes = productStyleColor["sizes"]
                                for size in sizes:
                                    item['skuList'].append(size["skuId"])
                
                #self.output_file = open('skuList.txt', 'a')
                #self.output_file.write(size["skuId"] + '\n')
                item['totalSkus'] = len(item['skuList'])
                break
        
        return isProductDataLoaded, item

    def extractSkusForStyle(self, response):
        try :
            url = response.meta.get('url')
            div_name = response.meta.get('div_name')
            cat_name = response.meta.get('cat_name')
            delivery_tag = response.meta.get('delivery_tag')
            pattern = re.compile('gap.pageProductData = {(.*?)};')
            soup = BeautifulSoup(response.body.decode('utf-8'), 'lxml')
            scripts = soup.find_all('script')
            isProductDataLoaded, item = self.generateItem(url, pattern, scripts)
                        
            if(isProductDataLoaded):  
                self.channel.basic_ack(delivery_tag)      
                return item 
            else : 
                if('OutOfStockNoResults' in response.url) :
                    logging.warning('Product out-of-stock ! '+ str(response.url))
                    self.push_url_to_queue(url, div_name, cat_name)
                    self.channel.basic_ack(delivery_tag)
                else:    
                    self.channel.basic_nack(delivery_tag)
        except Exception as inst:
            logging.error('Exception while processing category contents '+ str(inst)) 
            self.channel.basic_nack(delivery_tag)        
       
    def handle_error(self, failure):
        url = failure.request._url if failure.request._url else failure.request._original_url
        logging.error('Exception while rendering page URL: %s, Failure type: %s', url, failure.type)
        delivery_tag = failure.request.meta.get('delivery_tag')
        self.channel.basic_nack(delivery_tag)

        
        
    def push_url_to_queue(self,url,div_name,cat_name):    
          headers={'div_name':div_name,'cat_name': cat_name}
          RabbitMQUtil.push_message_to_queue(self.channel, url, headers, self.out_of_stock_products_queue)
     
    
    def initializeMongoDB(self):
        self.mongo_uri = self.settings.get(Constants.MONGO_URI, None)
        self.mongo_db = self.settings.get(Constants.MONGO_DATABASE, None)
        self.client = MongoDBUtil.get_mongo_client(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def initializeRabbitMQ(self):
        self.connection = RabbitMQUtil.get_connection(self.settings)
        self.channel = self.connection.channel()
        self.inbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.PRODUCTS.upper())
        self.out_of_stock_products_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.OUT_OF_STOCK_PRODUCTS.upper()) 
        
        RabbitMQUtil.declare_queue(self.channel, self.inbound_queue, True)
        RabbitMQUtil.declare_queue(self.channel, self.out_of_stock_products_queue, True)
        
        

    def initializeBaseProperties(self, kwargs):
        self.brand = kwargs.get(Constants.BRAND).upper() if kwargs.get(Constants.BRAND) else Constants.EMPTY_STRING
        self.division = kwargs.get(Constants.DIVISION).upper() if kwargs.get(Constants.DIVISION) else Constants.EMPTY_STRING
        self.category = kwargs.get(Constants.CATEGORY).upper() if kwargs.get(Constants.CATEGORY) else Constants.EMPTY_STRING
        self.domain_name = self.settings.get(self.brand + Constants.UNDERSCORE + Constants.DOMAIN_NAME, None)
        self.runner = kwargs.get(Constants.RUNNER)
        self.queue_purge_flag = kwargs.get(Constants.QUEUE_PURGE_FLAG)
        self.division_count = self.settings.get(Constants.PRODUCT_COUNT_PER_PAGE, None)  
        
        #self.custom_settings['FEED_URI'] = self.brand+'_skus.csv'
        
        
    def closeConnections(self):
        self.connection.close()
        self.client.close()         
