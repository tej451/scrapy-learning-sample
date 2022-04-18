import scrapy.cmdline

def main():
   # scrapy.cmdline.execute(argv=['scrapy', 'runspider', 'SkuSpider.py', '-s JOBDIR=crawls/SkuSpider-1'])
    scrapy.cmdline.execute(argv=['scrapy', 'runspider', 'BaseSpider.py', '-a' 'category=Innovation Studio', '-a' 'division=men', '-a' 'brand=gap'])
     

if  __name__ =='__main__':
    main() 
