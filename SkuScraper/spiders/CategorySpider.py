
# encoding=utf8
import sys
import scrapy
from scrapy_splash import SplashRequest
import logging
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
try: #python 3
    from urllib import parse
except ImportError: #python 2
     from urlparse  import urlparse 
     from urlparse import parse_qs
from SkuScraper.spiders.ProductSpider import ProductSpider
from SkuScraper.common import Constants
from SkuScraper.common.utils.mq.RabbitMQUtil import RabbitMQUtil
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
from SkuScraper.common.utils.XpathUtil import XpathUtil
from SkuScraper.common.utils.LuaUtil import LuaUtil
   
class CategorySpider(scrapy.Spider):
    name = Constants.CATEGORY_SPIDER_NAME
    settings = Settings(get_project_settings())
    http_user = settings.get(Constants.HTTP_USER, None)
    http_pass = settings.get(Constants.HTTP_PASSWORD, None)
   
    custom_settings = settings.get(Constants.CATEGORY_SPIDER_CUSTOM_SETTINGS, None)
   
    def __init__(self, *args, **kwargs):
        super(CategorySpider, self).__init__(*args, **kwargs)
        self.spider_params = kwargs.get(Constants.SPIDER_PARAMS)
        self.initializeBaseProperties(self.spider_params)
        self.initializeMongoDB()
        self.initializeRabbitMQ() 
   
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CategorySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        logging.info("####### Category spider opened #######")
        if self.queue_purge_flag :
            RabbitMQUtil.purge_queue(self.channel, self.outbound_queue); # Purge all outbound queues
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = False

    def spider_closed(self, spider):
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, True)
        if q_len !=0 :
            self.runner.crawl(CategorySpider,spider_params=self.spider_params)
        else :
            logging.info("####### Category spider closed #######")
            self.closeConnections()
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = True
            self.runner.crawl(ProductSpider,spider_params=self.spider_params) 

    
    def start_requests(self):
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
        while q_len !=0 :
            method_frame, header_frame, body = self.channel.basic_get(
                          queue=self.inbound_queue,
                          no_ack=False) 
            url = body.decode()
            div_name = header_frame.headers.get('div_name')
            delivery_tag = method_frame.delivery_tag
            logging.info(" [x] Received division %r" % url)
            q_len = RabbitMQUtil.get_queue_size(self.channel, self.inbound_queue, False)
            yield SplashRequest(url, self.parse_category_contents, args={'wait': 0.5, 'timeout': 300, 'lua_source': LuaUtil.get_category_lua_script(self.brand,self.category)}, errback=self.handle_error, meta={'div_name': div_name, 'delivery_tag':delivery_tag})




    def parse_category_contents(self, response):  
       try :
             div_name = response.meta.get('div_name')
             delivery_tag = response.meta.get('delivery_tag')  
             if(not self.division):
                 division_name = div_name 
             else:
                 division_name = self.division     
             categoryList = XpathUtil.get_category_list(self.brand, division_name, self.category, response)
             category_dict = {}
             categoryid_dict = {}
             for category in categoryList:
                cat_name_span =  XpathUtil.get_category_name(self.brand, division_name, category)
                cat_name = cat_name_span[0].upper().strip().encode('ascii', 'ignore').decode('ascii')
                if(cat_name not in self.skip_categories):
                    href = category.xpath('@href').extract()
                    url = response.urljoin(href[0])
                    try:
                        #python2
                        category_id = parse_qs(urlparse(url).query)['cid'][0]
                    except Exception:    
                        #python3
                        category_id = parse.parse_qs(parse.urlparse(url).query)['cid'][0]
                    category_dict.update({str(cat_name) : str(url)})
                    categoryid_dict.update({str(cat_name) : category_id})
             self.collectCategoryURLs(div_name, delivery_tag, category_dict, categoryid_dict, cat_name)             
       except Exception as inst:
            logging.error('Exception while fetching category URLs '+ str(inst)) 
            self.channel.basic_nack(delivery_tag)    
                     
    def handle_error(self, failure):
        url = failure.request._original_url if failure.request._original_url else failure.request._url
        logging.error('Exception while rendering page URL: %s, Failure type: %s', url, failure.type)
        delivery_tag = failure.request.meta.get('delivery_tag')
        self.channel.basic_nack(delivery_tag)
                     
        
    def push_url_to_queue(self,url,div_name,cat_name,cat_id,target_queue):  
         headers={'div_name':div_name,'cat_name': cat_name, 'cat_id': cat_id}
         RabbitMQUtil.push_message_to_queue(self.channel, url, headers, target_queue)  
         

    def collectCategoryURLs(self, div_name, delivery_tag, category_dict, categoryid_dict, cat_name):
        if not self.category:
            for cat_name, cat_url in category_dict.items():
                cat_id = categoryid_dict[cat_name]
                self.push_url_to_queue(cat_url, div_name, cat_name, cat_id, self.outbound_queue)
        elif str(self.category) in category_dict:
            self.push_url_to_queue(category_dict.get(self.category), div_name, self.category, categoryid_dict.get(self.category), self.outbound_queue)
        else:
            logging.error('The crawl criteria dosent match --> Category : %s', self.category)
        #TO-DO: Check for category count and send Ack
        self.channel.basic_ack(delivery_tag)        
    
    
    
    
        
    def initializeMongoDB(self):
        self.mongo_uri = self.settings.get(Constants.MONGO_URI, None)
        self.mongo_db = self.settings.get(Constants.MONGO_DATABASE, None)
        self.client = MongoDBUtil.get_mongo_client(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def initializeRabbitMQ(self):
        self.connection = RabbitMQUtil.get_connection(self.settings)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.inbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.DIVISION.upper())
        self.outbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.CATEGORY.upper())
        RabbitMQUtil.declare_queue(self.channel, self.inbound_queue, True)
        RabbitMQUtil.declare_queue(self.channel, self.outbound_queue, True)
        
         


    def initializeBaseProperties(self, kwargs):
        self.brand = kwargs.get(Constants.BRAND).upper() if kwargs.get(Constants.BRAND) else Constants.EMPTY_STRING
        self.division = kwargs.get(Constants.DIVISION).upper() if kwargs.get(Constants.DIVISION) else Constants.EMPTY_STRING
        self.category = kwargs.get(Constants.CATEGORY).upper() if kwargs.get(Constants.CATEGORY) else Constants.EMPTY_STRING
        self.domain_name = self.settings.get(self.brand + Constants.UNDERSCORE + Constants.DOMAIN_NAME, None)
        self.runner = kwargs.get(Constants.RUNNER)
        self.queue_purge_flag = kwargs.get(Constants.QUEUE_PURGE_FLAG)
        self.division_count = self.settings.get(Constants.PRODUCT_COUNT_PER_PAGE, None)  
        self.skip_categories = self.settings.get(self.brand + Constants.UNDERSCORE + Constants.SKIP_CATEGORIES, None)
        self.skip_categories = [item.upper() for item in self.skip_categories]  
        
        
    def closeConnections(self):
        self.connection.close()
        self.client.close() 
           
            
