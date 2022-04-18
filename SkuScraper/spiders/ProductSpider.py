
from scrapy.selector import Selector
import scrapy
from scrapy_splash import SplashRequest
import logging
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
from scrapy.settings import Settings
try: #python 3
    from urllib.parse import urlparse
    from urllib.parse import parse_qs
except ImportError: #python 2
     from urlparse  import urlparse 
     from urlparse import parse_qs
from time import time
from scrapy.exceptions import DontCloseSpider
from SkuScraper.spiders.ProductScraper import ProductScraper
from SkuScraper.common import Constants
from SkuScraper.common.utils.mq.RabbitMQUtil import RabbitMQUtil
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
from SkuScraper.common.utils.XpathUtil import XpathUtil
from SkuScraper.common.utils.LuaUtil import LuaUtil
   
class ProductSpider(scrapy.Spider):
    name = Constants.PRODUCT_SPIDER_NAME
    settings = Settings(get_project_settings())
    http_user = settings.get(Constants.HTTP_USER, None)
    http_pass = settings.get(Constants.HTTP_PASSWORD, None)
    custom_settings = settings.get(Constants.PRODUCT_SPIDER_CUSTOM_SETTINGS, None)

   
    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.spider_params = kwargs.get(Constants.SPIDER_PARAMS)
        self.initializeBaseProperties(self.spider_params)
        self.initializeMongoDB()
        self.initializeRabbitMQ() 
        
   
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ProductSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        #crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider
    
    def spider_opened(self, spider):
        logging.info("####### Product spider opened  ####### ")
        if self.queue_purge_flag :
            RabbitMQUtil.purge_queue(self.channel, self.outbound_queue);# Purge all outbound queues
            RabbitMQUtil.purge_queue(self.channel, self.filtered_url_queue);
            RabbitMQUtil.purge_queue(self.channel, self.error_queue);
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = False

    def spider_closed(self, spider):
        #self.channel.close(reply_code=0, reply_text="Normal shutdown")
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, True)
        if q_len !=0 :
            self.runner.crawl(ProductSpider,spider_params=self.spider_params)
        else :
            logging.info("#######  Product spider closed ####### ")
            self.closeConnections()
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = True
            self.runner.crawl(ProductScraper,spider_params=self.spider_params)

    def spider_idle(self, spider):
        logging.info("#######  Product spider idle ####### ")  
        q = self.channel.queue_declare(self.inbound_queue,durable=True)
        self.channel.basic_recover(q)
        #raise DontCloseSpider 

    def start_requests(self):
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
        while q_len !=0 :
            method_frame, header_frame, body = self.channel.basic_get(
                          queue=self.inbound_queue,
                          no_ack=False) 
            url = body.decode()
            div_name = header_frame.headers.get('div_name')
            cat_name = header_frame.headers.get('cat_name')
            cat_id = header_frame.headers.get('cat_id')
            cat_last_page_product_count = header_frame.headers.get('cat_last_page_product_count')
            delivery_tag = method_frame.delivery_tag
            scarped_product_count = 0
            #self.categoryProductCount[cat_id] = []
            logging.info(" [x] Received category %r" % url)
            q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
            yield SplashRequest(url, self.parse_product_contents, endpoint='execute',dont_filter=True,args={'wait': 0.5, 'timeout': 300, 'lua_source': LuaUtil.get_prodcuts_lua_script(self.brand,self.category)}, errback=self.handle_error, meta={'div_name':div_name,'cat_name': cat_name,'cat_id':cat_id, 'delivery_tag':delivery_tag, 'scarped_product_count':scarped_product_count,'cat_last_page_product_count':cat_last_page_product_count,'url':url})

    
    def acknowledgeMessage(self, delivery_tag):
        if str(self.scarped_product_count) == self.totalProducts:
            self.channel.basic_ack(delivery_tag)
        else:
            self.channel.basic_nack(delivery_tag)
             


    def pushProductURLtoQueue(self, response, div_name, cat_name, productList):
        for product in productList:
            href = product.xpath('@href').extract()
            url = response.urljoin(href[0])
            productURLQueryParamsDict =  parse_qs(urlparse(url).query)
            if 'pid' in productURLQueryParamsDict :
              self.push_url_to_queue(url, div_name, cat_name)
            else: 
              self.push_filtered_urls_to_queue(url, div_name, cat_name)    
            
    def push_message_to_queue(self,url,div_name,cat_name,cat_id,target_queue):  
         headers={'div_name':div_name,'cat_name': cat_name, 'cat_id': cat_id}
         RabbitMQUtil.push_message_to_queue(self.channel, url, headers, target_queue)          


    def getTotalProducts(self, response):
        itemCountSpan = Selector(response).xpath('//div[@class="tabs--item-count cat-page--item-count"]//span')
        if(itemCountSpan):
          totalProductCount = itemCountSpan[0].xpath('text()').extract()[0]
        else:
          totalProductCount = int(0)
        return totalProductCount
        #return Selector(response).xpath('//div[@class="tabs--item-count cat-page--item-count"]//span')[0].xpath('text()').extract()[0]


    def getCurrentPage(self, response):
        currentPageSpan = Selector(response).xpath('//div[@class="basic-pagination"]//span[@class="basic-pagination--text"]//span[@data-bind="text: k_currentPageDisplay"]')
        if(currentPageSpan):
          currentPageIndex = currentPageSpan[0].xpath('text()').extract()[0]
        else:
          currentPageIndex = int(0)
        return currentPageIndex


    def getNoOfPages(self, response):
        noOfPagesSpan = Selector(response).xpath('//div[@class="basic-pagination"]//span[@class="basic-pagination--text"]//span[@data-bind="text: k_lastPage"]')
        if(noOfPagesSpan):
          noOfPages = noOfPagesSpan[0].xpath('text()').extract()[0]
        else:
          noOfPages = int(0)
        return noOfPages

    #TO-DO: Refactor
    def parse_product_contents(self, response):    
        try : 
             div_name = response.meta.get('div_name')
             cat_name = response.meta.get('cat_name') 
             cat_id = response.meta.get('cat_id')          
             delivery_tag = response.meta.get('delivery_tag')
             url = response.meta.get('url')
             self.scarped_product_count = response.meta.get('scarped_product_count')  
             cat_last_page_product_count = response.meta.get('cat_last_page_product_count')  
             productList = Selector(response).xpath('//div[@class="product-card-grid--all-groups"]//div[@class="product-card-grid--group"]//div[@class="grid-root grid ism-root"]//div[@class="g-1-2 g-lg-1-3 g-xl-1-3 g-1280-1-4"]//div[@class="g-inner grid-inner"]//div[@class="product-card"]//div[@class="product-card--body"]//a[@class="product-card--link"]')
             self.rendered_product_url_count = len(productList)
             self.totalProducts = self.getTotalProducts(response)
             currentPage = self.getCurrentPage(response)
             noOfPages = self.getNoOfPages(response)
             intCurrentPage = int(currentPage)
             intTotalProducts = int(self.totalProducts)
             intNoOfPages = int(noOfPages)
             #globals()[div_name+cat_id] =  []
             if (intNoOfPages > int(1)) : 
                 # check next page
                 if(intCurrentPage == int(1) and self.rendered_product_url_count == int(300)):
                     cat_last_page_product_count = intTotalProducts - (300*(intNoOfPages-1))
                     for  nextPage in range(1, intNoOfPages):    
                         queryParams = urlparse(response._url).query + '&sop=true'
                         parts = urlparse(response._url)._replace(query=queryParams,fragment='pageId='+str(nextPage))
                         print(" [x] URL %r" % parts.geturl())
                         logging.info(" [x] URL %r" % parts.geturl())
                         self.push_cat_pages_url_to_queue(parts.geturl(), div_name, cat_name, cat_id, cat_last_page_product_count)
                     self.pushProductURLtoQueue(response, div_name, cat_name, productList)      
                     self.channel.basic_ack(delivery_tag)
       
                 elif(intCurrentPage > int(1) and intCurrentPage < int(noOfPages) and self.rendered_product_url_count == int(300)) :  
                    self.pushProductURLtoQueue(response, div_name, cat_name, productList) 
                    self.channel.basic_ack(delivery_tag)
                 elif(intCurrentPage == int(noOfPages)): 
                     #if (self.rendered_product_url_count >= int(cat_last_page_product_count)):
                     if (self.rendered_product_url_count != int(0)):
                         self.pushProductURLtoQueue(response, div_name, cat_name, productList)     
                         self.channel.basic_ack(delivery_tag)
                     else:
                        self.channel.basic_nack(delivery_tag)   
                 elif(intCurrentPage > int(noOfPages)):
                     self.push_message_to_queue(url, div_name, cat_name, cat_id, self.error_queue)  
                     self.channel.basic_ack(delivery_tag) 
                 else:
                    self.channel.basic_nack(delivery_tag)           
                     
             elif (intNoOfPages == int(1) and self.rendered_product_url_count == int(self.totalProducts)) : 
                  self.pushProductURLtoQueue(response, div_name, cat_name, productList)  
                  self.channel.basic_ack(delivery_tag)  
             elif (intNoOfPages == int(0)) :
                  self.push_message_to_queue(url, div_name, cat_name, cat_id, self.error_queue)  
                  self.channel.basic_ack(delivery_tag)
             else :
                 self.channel.basic_nack(delivery_tag)
        except Exception as inst:
            logging.error('Exception while processing category contents '+ str(inst))
            self.channel.basic_nack(delivery_tag)
               
    def handle_error(self, failure):
        url = failure.request._original_url
        logging.error('Exception while rendering page URL: %s, Failure type: %s', url, failure.type)
        delivery_tag = failure.request.meta.get('delivery_tag')
        cat_id = failure.request.meta.get('cat_id')
        self.channel.basic_nack(delivery_tag)
                     
        
    def push_url_to_queue(self,url,div_name,cat_name):
          #with open('productURLs.txt', 'a') as outfile:
          #         outfile.write(str(url)+ '\n')     
          headers={'div_name':div_name,'cat_name': cat_name}
          RabbitMQUtil.push_message_to_queue(self.channel, url, headers, self.outbound_queue)
          self.scarped_product_count = self.scarped_product_count + 1
    
    def push_filtered_urls_to_queue(self,url,div_name,cat_name):    
          headers={'div_name':div_name,'cat_name': cat_name}
          RabbitMQUtil.push_message_to_queue(self.channel, url, headers, self.filtered_url_queue)
          
    def push_cat_pages_url_to_queue(self,url,div_name,cat_name,cat_id,cat_last_page_product_count): 
          headers={'div_name':div_name,'cat_name': cat_name, 'cat_id': cat_id, 'cat_last_page_product_count':cat_last_page_product_count}
          RabbitMQUtil.push_message_to_queue(self.channel, url, headers, self.inbound_queue)
        
   
    def initializeMongoDB(self):
        self.mongo_uri = self.settings.get(Constants.MONGO_URI, None)
        self.mongo_db = self.settings.get(Constants.MONGO_DATABASE, None)
        self.client = MongoDBUtil.get_mongo_client(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def initializeRabbitMQ(self):
        self.connection = RabbitMQUtil.get_connection(self.settings)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.inbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.CATEGORY.upper())
        self.outbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.PRODUCTS.upper())
        self.filtered_url_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.FILTERED_PRODUCTS.upper()) 
        self.error_queue = RabbitMQUtil.get_error_queue_name(self.settings, self.brand, Constants.CATEGORY.upper())
        RabbitMQUtil.declare_queue(self.channel, self.inbound_queue, True)
        RabbitMQUtil.declare_queue(self.channel, self.outbound_queue, True)
        RabbitMQUtil.declare_queue(self.channel, self.filtered_url_queue, True)
        RabbitMQUtil.declare_queue(self.channel, self.error_queue, True)
        
        
        
        
       


    def initializeBaseProperties(self, kwargs):
        self.brand = kwargs.get(Constants.BRAND).upper() if kwargs.get(Constants.BRAND) else Constants.EMPTY_STRING
        self.division = kwargs.get(Constants.DIVISION).upper() if kwargs.get(Constants.DIVISION) else Constants.EMPTY_STRING
        self.category = kwargs.get(Constants.CATEGORY).upper() if kwargs.get(Constants.CATEGORY) else Constants.EMPTY_STRING
        self.domain_name = self.settings.get(self.brand + Constants.UNDERSCORE + Constants.DOMAIN_NAME, None)
        self.runner = kwargs.get(Constants.RUNNER)
        self.queue_purge_flag = kwargs.get(Constants.QUEUE_PURGE_FLAG)
        self.division_count = self.settings.get(Constants.PRODUCT_COUNT_PER_PAGE, None)  
        
        
    def closeConnections(self):
        self.connection.close()
        self.client.close()      
        
     
            
