# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = SkuScraper.settings']},
    install_requires=[
        'scrapy',
        'scrapy_splash',
        'bs4',
        'pymongo',
        'scrapy_crawlera',
        'pika',
        'paramiko'
    ],
)


