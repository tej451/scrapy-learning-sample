


EMPTY_STRING = ''
ERROR ='ERROR'
HTTP_USER = 'HTTP_USER'
HTTP_PASSWORD = 'HTTP_PASSWORD'


BRAND = 'brand'
DIVISION = 'division'
CATEGORY = 'category'
PRODUCTS = 'products'
RUNNER = 'runner'
QUEUE_PURGE_FLAG = 'queue_purge_flag'
FILTERED_PRODUCTS = 'filtered_products'
OUT_OF_STOCK_PRODUCTS = 'out_of_stock_products'

MONGO_URI = 'MONGO_URI'
MONGO_DATABASE = 'MONGO_DATABASE'
PRODUCT_COUNT_PER_PAGE = 'PRODUCT_COUNT_PER_PAGE'

RABBITMQ_CONNECTION_PARAMETERS = 'RABBITMQ_CONNECTION_PARAMETERS'
RABBITMQ_USER = 'RABBITMQ_USER'
RABBITMQ_PASSWORD = 'RABBITMQ_PASSWORD'
RABBITMQ_HOST = 'RABBITMQ_HOST'
RABBITMQ_SOCKET_TIMEOUT = 'RABBITMQ_SOCKET_TIMEOUT'


SFTP_USER = 'SFTP_USER'
SFTP_PASSWORD = 'SFTP_PASSWORD'
SFTP_HOST = 'SFTP_HOST'
SFTP_FILE_PATH = 'SFTP_FILE_PATH'


BASE_SPIDER_NAME = 'BaseSpider'
DIVISION_SPIDER_NAME = 'DivisionSpider'
CATEGORY_SPIDER_NAME = 'CategorySpider'
PRODUCT_SPIDER_NAME = 'ProductSpider'
PRODUCT_SCRAPER_NAME = 'ProductScraper'


BASE_SPIDER_CUSTOM_SETTINGS = 'BASE_SPIDER_CUSTOM_SETTINGS'
DIVISION_SPIDER_CUSTOM_SETTINGS = 'DIVISION_SPIDER_CUSTOM_SETTINGS'
CATEGORY_SPIDER_CUSTOM_SETTINGS = 'CATEGORY_SPIDER_CUSTOM_SETTINGS'
PRODUCT_SPIDER_CUSTOM_SETTINGS = 'PRODUCT_SPIDER_CUSTOM_SETTINGS'
PRODUCT_SCRAPER_CUSTOM_SETTINGS = 'PRODUCT_SCRAPER_CUSTOM_SETTINGS'


QUEUE_SUFFIX = 'Q'
UNDERSCORE = "_"
SKIP_CATEGORIES = 'SKIP_CATEGORIES'
SKIP_DIVISIONS = 'SKIP_DIVISIONS'
SPIDER_PARAMS = 'spider_params'

DOMAIN_NAME = 'DOMAIN_NAME'
GAP = 'GAP'
ON = 'ON'
BR = 'BR'
ATHLETA = 'ATHLETA'
FACTORY_GAP = 'FACTORY_GAP'
FACTORY_BR = 'FACTORY_BR'


LUA_SCRIPT_CATEGORY_PRODUCT_LOAD = """function main(splash)
                                local num_scrolls = 10
                                local scroll_delay = 0.5
                                splash.images_enabled = false
                                splash:set_viewport_size(1980, 8020)
                                splash:on_request(function(request)
                                        if string.find(request.url, ".css") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.url, ".html") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.method, "POST") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.url, ".js") ~= nil then
                                            if string.find(request.url, "static_content") == nil then
                                               request.abort()
                                            end 
                                        end
                                    end)
                                local scroll_to = splash:jsfunc("window.scrollTo")
                                local get_body_height = splash:jsfunc(
                                    "function() {return document.body.scrollHeight;}"
                                )
                                assert(splash:go(splash.args.url))
                                --splash:set_viewport_full()
                                splash:wait(1)
                                --while not splash:select('span.icon-x') do
                                --  splash:wait(0.5)
                                --end
                                splash:runjs("jQuery('span.icon-x').click();")
                                --splash:wait(10)
                                local scroll_size = (get_body_height() / 10)
                               local initial_scroll_size = 0
                               local difference_scroll_size = scroll_size
                                     for _ = 1, num_scrolls do
                                        scroll_to(initial_scroll_size, initial_scroll_size + difference_scroll_size)
                                        splash:wait(scroll_delay)
                                        initial_scroll_size = initial_scroll_size + difference_scroll_size
                                    end  
                                return { 
                                    --png = splash:png(),
                                    html = splash:html(),
                                    --har = splash:har()
                                   }
                            end""" 
                            
LUA_SCRIPT_COMMON = """function main(splash)
                                    splash.images_enabled = false
                                    splash.js_enabled = false
                                    --splash.allowed_content_types = 'text/html'
                                    splash:on_request(function(request)
                                        if string.find(request.url, ".css") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.url, ".html") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.method, "POST") ~= nil then
                                            request.abort()
                                        end
                                    end)
                                    assert(splash:go(splash.args.url))
                                    --while not splash:select('span.icon-x') do
                                    --  splash:wait(0.5)
                                    --end
                                    splash:runjs("jQuery('span.icon-x').click();")
                                    --splash:wait(10)
                                    return { 
                                        html = splash:html(),
                                       }
                                end""" 
                                
                                
                                
LUA_SCRIPT_CATEGORY_PRODUCT_LOAD_BR_FACTORY = """function main(splash)
                                local num_scrolls = 10
                                local scroll_delay = 0.5
                                splash.images_enabled = false
                                splash:set_viewport_size(1980, 8020)
                                splash:on_request(function(request)
                                        if string.find(request.url, ".css") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.method, "POST") ~= nil then
                                            request.abort()
                                        end
                                        if string.find(request.url, ".js") ~= nil then
                                            if string.find(request.url, "static_content") == nil then
                                               request.abort()
                                            end 
                                        end
                                    end)
                                local scroll_to = splash:jsfunc("window.scrollTo")
                                local get_body_height = splash:jsfunc(
                                    "function() {return document.body.scrollHeight;}"
                                )
                                assert(splash:go(splash.args.url))
                                --splash:set_viewport_full()
                                splash:wait(1)
                                --while not splash:select('span.icon-x') do
                                --  splash:wait(0.5)
                                --end
                                splash:runjs("jQuery('span.icon-x').click();")
                                --splash:wait(10)
                                local scroll_size = (get_body_height() / 10)
                               local initial_scroll_size = 0
                               local difference_scroll_size = scroll_size
                                     for _ = 1, num_scrolls do
                                        scroll_to(initial_scroll_size, initial_scroll_size + difference_scroll_size)
                                        splash:wait(scroll_delay)
                                        initial_scroll_size = initial_scroll_size + difference_scroll_size
                                    end  
                                return { 
                                    --png = splash:png(),
                                    html = splash:html(),
                                    --har = splash:har()
                                   }
                            end"""                                 