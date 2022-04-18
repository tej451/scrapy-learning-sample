import scrapy
from scrapy_splash import SplashRequest
import logging
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy.contrib.spiders import CrawlSpider
from SkuScraper.spiders.CategorySpider import CategorySpider
from SkuScraper.common import Constants
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from SkuScraper.spiders.DivisionSpider import DivisionSpider
from scrapy.exceptions import CloseSpider
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
import datetime
import os
import paramiko

   
class BaseSpider(CrawlSpider):
    name = Constants.BASE_SPIDER_NAME
    settings = Settings(get_project_settings())
    runner = CrawlerRunner(get_project_settings())
    custom_settings = settings.get(Constants.BASE_SPIDER_CUSTOM_SETTINGS, None)
    reactor1 = reactor
      
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        logging.info("####### Base spider opened #######")


    def spider_closed(self, spider):
         logging.info("####### Base spider closed #######")
         self.d.addBoth(lambda _: reactor.stop()) #@UndefinedVariable 
         
    def start_requests(self):
        urls = [
             "www.google.com"
        ]
        for url in urls:
            yield scrapy.Request(str(url), self.parse)     

    def parse(self, response):
        logging.info("####### Base spider parse #######")
        

    def setInitParameters(self, brand, division, category):
        self.brand = brand
        self.division = division
        self.category = category
        self.collection_name = self.brand + '_'+ 'SKUS'+ '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-1]



    def copyFileToRemotePath(self, settings, output_file):
        local_file_path = os.path.realpath(output_file.name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(settings.get(Constants.SFTP_HOST), username=settings.get(Constants.SFTP_USER), password=settings.get(Constants.SFTP_PASSWORD))
        sftp = ssh.open_sftp()
        remote_path = settings.get(Constants.SFTP_FILE_PATH)
        file_name = self.brand + '_unique_sku_list.txt'
        sftp.put(local_file_path, remote_path + file_name)
        sftp.close()
        ssh.close()

    def generateUniqueSkuListFile(self):
        settings = get_project_settings()
        mongo_uri = settings.get(Constants.MONGO_URI, None)
        mongo_db = settings.get(Constants.MONGO_DATABASE, None)
        client = MongoDBUtil.get_mongo_client(mongo_uri)
        db = client[mongo_db]
        output_file = open(self.brand+'_unique_sku_list.txt', 'w')
        uniqueSkuList = db[self.collection_name].distinct("skuList")
        
        if(uniqueSkuList):
            logging.info("####### Writing Unique SKUs to local file #######")
            for sku in uniqueSkuList:
                output_file.write(sku + '\n') 
            logging.info("####### Copying Unique SKUs to remote file #######")    
            self.copyFileToRemotePath(settings, output_file)     

    def __init__(self, brand=None, division=None, category=None, *args, **kwargs):
        self.setInitParameters(brand, division, category)
        self.crawl()
        reactor.run() #@UndefinedVariable  
        self.generateUniqueSkuListFile()
        os._exit(0) #Intentionally using "os exit" to prevent further process as this spider purpose is just to trigger other spider chain
        
    @defer.inlineCallbacks
    def crawl(self):
        spider_params_gap = { 'brand' : self.brand, 'division' : self.division, 'category':self.category,'collection_name': self.collection_name, 'runner': BaseSpider.runner, 'queue_purge_flag': True}
        logging.info("Initiated Crawling for %s", spider_params_gap)
        yield BaseSpider.runner.crawl(DivisionSpider,spider_params=spider_params_gap)
        #yield runner.crawl(DivisionSpider,spider_params=spider_params_br)
        self.d = BaseSpider.runner.join()
        self.d.addBoth(lambda _: reactor.stop()) #@UndefinedVariable 
        
      
        
              
        
  

    
    
    
   
      
      
        
     
           
            
