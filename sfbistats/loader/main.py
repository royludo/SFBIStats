# coding=utf-8

import email
import os
import re
import urllib2
from HTMLParser import HTMLParser
from pprint import pprint

import pymongo
from scrapy.crawler import CrawlerProcess

import job_offer
import spider
from sfbi_parser import EmlParser



class MongoDBStorage(object):
    def process_item(self, item, spider):
        #job_collection.insert_one(item)
        print "mongo-> "+str(item)
        return item

'''
    clean mongodb stuff
'''
def clear_db(client):
    print "Start cleaning DB"
    client.drop_database(db_name)
    print "DB " + db_name + " now clean"

db_name = 'sfbi_jobs'
mongo_client = pymongo.MongoClient()
sfbi_db = mongo_client[db_name]
job_collection = sfbi_db['jobs']

mailDirectory = "/home/ludovic/Programs/Projects/SFBIStats/resources/mails"
parser = EmlParser(mailDirectory)
link_list = parser.get_link_list()

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'DOWNLOAD_DELAY': 0.5,
    'COOKIES_ENABLED': False,
    'ITEM_PIPELINES': {'__main__.MongoDBStorage': 1}
})

process.crawl(spider.JobSpider, start_urls=link_list[1:10])
process.start() # the script will block here until the crawling is finished

#clear_db(mongo_client)

