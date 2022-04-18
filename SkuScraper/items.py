# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from bson.objectid import ObjectId


class SkuscraperItem(scrapy.Item):
    # define the fields for your item here like:
     # response = scrapy.Field()
     brand = scrapy.Field()
     name = scrapy.Field()
     styleId = scrapy.Field()
     categoryId = scrapy.Field()
     skuList = scrapy.Field()
     totalSkus = scrapy.Field()
     url = scrapy.Field()
     
     
class CrawlerItem(scrapy.Item):     
     name = scrapy.Field()
     link = scrapy.Field()