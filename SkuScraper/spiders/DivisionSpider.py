import scrapy
from scrapy_splash import SplashRequest
import logging
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy.contrib.spiders import CrawlSpider
from SkuScraper.spiders.CategorySpider import CategorySpider
from SkuScraper.common import Constants
from SkuScraper.common.utils.mq.RabbitMQUtil import RabbitMQUtil
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
from SkuScraper.common.utils.XpathUtil import XpathUtil
from SkuScraper.common.utils.LuaUtil import LuaUtil
   
class DivisionSpider(CrawlSpider):
    name = Constants.DIVISION_SPIDER_NAME
    settings = Settings(get_project_settings())
    http_user = settings.get(Constants.HTTP_USER, None)
    http_pass = settings.get(Constants.HTTP_PASSWORD, None)
    
    custom_settings = settings.get(Constants.DIVISION_SPIDER_CUSTOM_SETTINGS, None)
   

    def __init__(self, *args, **kwargs):
        super(DivisionSpider, self).__init__(*args, **kwargs)
        self.spider_params = kwargs.get(Constants.SPIDER_PARAMS)
        if(not self.spider_params):
            logging.error('Please enter spider parameters : brand,division,categry etc')
            raise Exception("Please enter spider parameters : brand,division,categry etc")
        self.initializeBaseProperties(self.spider_params)
        self.initializeMongoDB()
        self.initializeRabbitMQ()  
        
   
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DivisionSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        logging.info("####### Division spider opened #######")
        if self.queue_purge_flag :
            RabbitMQUtil.purge_queue(self.channel, self.outbound_queue); # Purge all outbound queues
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = False
       



    def spider_closed(self, spider):
        q_len = RabbitMQUtil.get_queue_size(self.channel, self.outbound_queue, True)
        if q_len == 0 :
            self.runner.crawl(DivisionSpider,spider_params=self.spider_params)
        else :
            logging.info("####### Division spider closed #######")
            self.closeConnections()
            self.spider_params[Constants.QUEUE_PURGE_FLAG] = True
            self.runner.crawl(CategorySpider,spider_params=self.spider_params)

    
    def start_requests(self):
        urls = [
             self.domain_name
        ]
        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5, 'timeout': 300, 'lua_source': LuaUtil.get_division_lua_script(self.brand,self.division)},errback=self.handle_error)



    def parse(self, response):  # Scrap Divisions/Sub-Divisions
        try:
                divisionList = XpathUtil.get_division_list(self.brand,response)
                division_dict = {}
                for division in divisionList:
                    name = division.xpath('text()').extract()
                    href = division.xpath('@href').extract()
                    url = response.urljoin(href[0]).strip()
                    if(name[0].upper().strip() not in self.skip_divisions):
                      division_dict.update({str(name[0].upper().strip()) : str(url)})
                self.collectDivisionURLs(division_dict, url)   
        except Exception as inst:
            logging.error('Exception while fetching division URLs '+ str(inst)) 
            
                     
    def handle_error(self, failure):
        url = failure.request._original_url if failure.request._original_url else failure.request._url
        logging.error('Exception while rendering page URL: %s, Failure type: %s', url, failure.type)
        
    def collectDivisionURLs(self, division_dict, url):
        if not self.division:
            for div_name, url in division_dict.items():
                self.push_url_to_queue(url, div_name, self.outbound_queue)
        
        elif str(self.division) in division_dict:
            self.push_url_to_queue(division_dict.get(self.division), self.division, self.outbound_queue)
        else:
            logging.error('The crawl criteria dosent match --> Division : %s', self.division)    
        
    def push_url_to_queue(self,url,div_name,target_queue):    
        headers={'div_name': div_name}
        RabbitMQUtil.push_message_to_queue(self.channel, url, headers, target_queue)
        
        
    def initializeMongoDB(self):
        self.mongo_uri = self.settings.get(Constants.MONGO_URI, None)
        self.mongo_db = self.settings.get(Constants.MONGO_DATABASE, None)
        self.client = MongoDBUtil.get_mongo_client(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def initializeRabbitMQ(self):
        self.connection = RabbitMQUtil.get_connection(self.settings)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.outbound_queue = RabbitMQUtil.get_queue_name(self.settings, self.brand, Constants.DIVISION.upper())
        RabbitMQUtil.declare_queue(self.channel, self.outbound_queue, True)
        
        


    def initializeBaseProperties(self, kwargs):
        self.brand = kwargs.get(Constants.BRAND).upper() if kwargs.get(Constants.BRAND) else Constants.EMPTY_STRING
        self.division = kwargs.get(Constants.DIVISION).upper() if kwargs.get(Constants.DIVISION) else Constants.EMPTY_STRING
        self.category = kwargs.get(Constants.CATEGORY).upper() if kwargs.get(Constants.CATEGORY) else Constants.EMPTY_STRING
        self.domain_name = self.settings.get(self.brand + Constants.UNDERSCORE + Constants.DOMAIN_NAME, None)
        self.runner = kwargs.get(Constants.RUNNER)
        self.queue_purge_flag = kwargs.get(Constants.QUEUE_PURGE_FLAG)
        self.division_count = self.settings.get(Constants.PRODUCT_COUNT_PER_PAGE, None)  
        self.skip_divisions = self.settings.get(self.brand+ Constants.UNDERSCORE+ Constants.SKIP_DIVISIONS, None)
        self.skip_divisions = [item.upper() for item in self.skip_divisions]  
        
        
    def closeConnections(self):
        self.connection.close()
        self.client.close()    
      
      
        
     
           
            
