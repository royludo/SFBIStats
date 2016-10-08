# coding=utf-8
from __future__ import division, print_function, unicode_literals

import pymongo
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
import argparse
from sfbistats.loader import spider
from sfbistats.loader.sfbi_parser import EmlParser



class MongoDBStorage(object):
    """
    see http://doc.scrapy.org/en/latest/topics/item-pipeline.html#write-items-to-mongodb
    """

    def __init__(self, settings):
        self.db_name = settings.get('DB_NAME')
        mongo_client = pymongo.MongoClient()
        sfbi_db = mongo_client[self.db_name]
        self.job_collection = sfbi_db[settings.get('COLLECTION_NAME')]

    def process_item(self, item, spider):
        self.job_collection.insert_one(item)
        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

'''
    clean mongodb stuff
'''
def clear_db(client):
    print ("Start cleaning DB")
    client.drop_database(db_name)
    print ("DB " + db_name + " now clean")

if __name__ == '__main__':

    # parse and check arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--eml_dir', required=True)
    argparser.add_argument('--db_name', required=True)
    args = vars(argparser.parse_args())
    eml_dir = args['eml_dir']
    db_name = args['db_name']
    collection_name = 'jobs'
    configure_logging({'LOG_FILE': 'loader.log'})

    print ("Parsing mails...")
    parser = EmlParser.from_mbox(eml_dir)
    link_list = parser.get_link_list()

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'DOWNLOAD_DELAY': 0.5,
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {'__main__.MongoDBStorage': 1},
        # our specific settings
        'DB_NAME': db_name,
        'COLLECTION_NAME': collection_name,
        # take 301 redirection in count
        # doesn't seem to work, though :(
        # 'DOWNLOADER_MIDDLEWARES': {'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 1}
    })

    process.crawl(spider.JobSpider, start_urls=link_list)
    process.start() # the script will block here until the crawling is finished

    #clear_db(mongo_client)

