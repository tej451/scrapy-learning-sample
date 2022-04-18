import sys
import logging
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
#from SkuScraper.spiders.DivisionSpider import DivisionSpider
#from SkuScraper.spiders.ProductSpider import ProductSpider
#from SkuScraper.spiders.ProductScraper import ProductScraper
#from SkuScraper.spiders.CategorySpider import CategorySpider
from SkuScraper.common import Constants
from SkuScraper.common.utils.db.MongoDBUtil import MongoDBUtil
import csv
from SkuScraper import SpiderRunner


def main():    
    print("Test Main Module")
    #SpiderRunner.main()

if  __name__ =='__main__':
    main() 

    