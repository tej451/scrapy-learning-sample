
import pika
from SkuScraper.common import Constants
from scrapy.selector import Selector

class XpathUtil(object):    
    
  division_xpath_dict ={
      Constants.GAP : '//div[@id="mainNavGOL"]//ul[@class="gpnavigation"]/li[@class="topNavItem"]//a',
      Constants.BR : '//div[@id="mainNavBROL"]//ul[@class="brnavigation-brol heading-e"]//li[contains(@class, "topNavLink")]//a',
      Constants.ATHLETA: '//div[@class="topnav_atol"]//ul//li//a',
      Constants.FACTORY_GAP: '//div[@id="mainNavGFOL"]//ul[@class="gpnavigation"]/li[@class="topNavItem"]//a',
      Constants.FACTORY_BR:'//div[@id="mainNavBROL"]//ul[@class="brnavigation-brol sds_heading-e"]//li[contains(@class, "topNavLink")]//a'
      }  
    
  @staticmethod
  def get_division_list(brand,response):
      if(brand == Constants.ON):
        divisionList = Selector(response).css('.sds_g-2-24').xpath('a') #OldNavy
      else:    
         divisionList = Selector(response).xpath(XpathUtil.division_xpath_dict.get(brand))        
             
      return divisionList
  
  @staticmethod
  def get_category_list(brand,division,category,response):
      if(brand == Constants.BR) :
          categoryList = XpathUtil.getBRCategoryList(division, response)
      else:
         categoryList = Selector(response).xpath('//nav[@class="sidebar-navigation"]//div//a')    
      return categoryList
  

  @staticmethod
  def get_category_name(brand,division,category):
      if(brand == Constants.BR) :
          cat_name =XpathUtil.getBRCategoryName(division, category)
      else:
         cat_name = category.xpath('span/text()').extract()
      return cat_name
  
  
  
  
  @staticmethod
  def getBRCategoryList(division, response):
      if (division == 'SHOES'):
          categoryList = Selector(response).css('.sds_show-at-lg').xpath('a')
      elif (division == 'ACCESSORIES' or division == 'SALE'):
          categoryList = Selector(response).xpath('//nav[@class="sidebar-navigation"]//div//a')
      else:
          categoryList = Selector(response).xpath('//div[@class="dropdownMenu"]//div[@class="flyoutMenu-list"]//ul//li//a')
      return categoryList
  
  @staticmethod
  def getBRCategoryName(division, category):
      if (division == 'SHOES' or division == 'ACCESSORIES' or division == 'SALE'):
          cat_name = category.xpath('span/text()').extract()
      else:
          cat_name = category.xpath('div/span/text()').extract()
      return cat_name

  
  

        