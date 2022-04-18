import sys
import logging
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from SkuScraper.spiders.DivisionSpider import DivisionSpider
from SkuScraper.spiders.ProductSpider import ProductSpider
from SkuScraper.spiders.ProductScraper import ProductScraper
from SkuScraper.spiders.CategorySpider import CategorySpider
from SkuScraper.common import Constants
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
import csv


#configure_logging()
runner = CrawlerRunner(get_project_settings())
settings = get_project_settings()  
mongo_uri = settings.get(Constants.MONGO_URI, None)
mongo_db = settings.get(Constants.MONGO_DATABASE, None)
client = MongoDBUtil.get_mongo_client(mongo_uri)
db = client[mongo_db]

@defer.inlineCallbacks
def crawl():
    logging.info("Initiated Crawling for %s", str(sys.argv))
    spider_params = { 'brand' : 'TEST', 'division' :'men', 'category':'jeans','runner': runner}
    yield runner.crawl(DivisionSpider,spider_params=spider_params)
    #yield runner.crawl(ProductScraper,runner=runner)
    #yield runner.crawl(SkuScraper.spiders.SkuSpider.SkuSpider,division=sys.argv[1],category=sys.argv[2],runner=runner)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop()) #@UndefinedVariable

crawl()
reactor.run() #@UndefinedVariable

output_file = open('unique_sku_list.txt', 'w')
uniqueSkuList = db.scrapy_items.distinct("skuList")
for sku in uniqueSkuList:
    output_file.write(sku + '\n')  
    

    