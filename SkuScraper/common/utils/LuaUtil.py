
from SkuScraper.common import Constants

class LuaUtil(object):
    
  @staticmethod
  def get_division_lua_script(brand,division):
      return Constants.LUA_SCRIPT_COMMON
  
  
  @staticmethod
  def get_category_lua_script(brand,category):
      if(brand == Constants.BR or brand == Constants.FACTORY_BR) :
         lua_source = Constants.LUA_SCRIPT_CATEGORY_PRODUCT_LOAD
      else:   
         lua_source = Constants.LUA_SCRIPT_COMMON 
      return lua_source
  
  @staticmethod
  def get_prodcuts_lua_script(brand,category):
      
      if(brand == Constants.FACTORY_BR) :
         lua_source = Constants.LUA_SCRIPT_CATEGORY_PRODUCT_LOAD_BR_FACTORY
      else:   
         lua_source = Constants.LUA_SCRIPT_CATEGORY_PRODUCT_LOAD 
      return lua_source
  
  

        