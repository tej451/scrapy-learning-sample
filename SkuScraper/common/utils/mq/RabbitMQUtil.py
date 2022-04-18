
import pika
from SkuScraper.common import Constants

class RabbitMQUtil(object):
    
  @staticmethod
  def get_connection(settings):
      #connection = pika.BlockingConnection(pika.URLParameters(settings.get(Constants.RABBITMQ_CONNECTION_PARAMETERS, None)))
      credentials = pika.PlainCredentials(settings.get(Constants.RABBITMQ_USER), settings.get(Constants.RABBITMQ_PASSWORD))
      connection = pika.BlockingConnection(pika.ConnectionParameters(
      credentials=credentials,
        host=settings.get(Constants.RABBITMQ_HOST),
         socket_timeout=settings.get(Constants.RABBITMQ_SOCKET_TIMEOUT)))
      return connection
  
  @staticmethod
  def declare_queue(channel,target_queue, durablity_flag):
      channel.queue_declare(target_queue,durable=durablity_flag) 
      
  @staticmethod
  def purge_queue(channel,target_queue):
      channel.queue_purge(target_queue)    

  @staticmethod
  def push_message_to_queue(channel,message,header_params,target_queue):    
      exchane = ''
      url_stripped = message.strip(' \n\r')
      channel.basic_publish(exchane,target_queue,url_stripped,
                                pika.BasicProperties(content_type='text/plain',delivery_mode=2,headers=header_params)
                                )
      
      
  @staticmethod
  def get_queue_size(channel,target_queue, recovery_flag):    
        q = channel.queue_declare(target_queue,durable=True)
        if recovery_flag:
          channel.basic_recover(q)
        q_len = q.method.message_count
        return q_len
        
        
  @staticmethod
  def get_queue_name(settings,brand,name):
      queue_name = settings.get(brand + Constants.UNDERSCORE + name + Constants.UNDERSCORE + Constants.QUEUE_SUFFIX, None)    
      return queue_name
  
  @staticmethod
  def get_error_queue_name(settings,brand,name):
      queue_name = settings.get(brand + Constants.UNDERSCORE + name + Constants.UNDERSCORE + Constants.ERROR + Constants.UNDERSCORE+ Constants.QUEUE_SUFFIX, None)    
      return queue_name
        