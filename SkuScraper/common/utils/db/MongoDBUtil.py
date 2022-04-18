
import pymongo
from SkuScraper.common import Constants

class MongoDBUtil(object):
    
  @staticmethod
  def get_mongo_client(mongo_uri):
      mongo_client = pymongo.MongoClient(mongo_uri)
      return mongo_client
  
  
        