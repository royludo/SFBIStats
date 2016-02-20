import re
from HTMLParser import HTMLParser

import scrapy

import job_offer


class JobSpider(scrapy.Spider):
    name = "pparker"
    #start_urls = ['http://www.sfbi.fr/content/stage-m1-d%C3%A9veloppement-doutils-pour-l%C3%A9cotoxicologie']

    def __init__(self, start_urls=None):
        super(JobSpider, self).__init__()
        #print "start_urls "+str(start_urls)
        self.start_urls = start_urls


    def parse(self, response):
        '''
            given html code, get the interesting section
        '''
        flag = 0
        parser = HTMLParser()
        stripper = HTMLStripper()
        # decode is important for utf-8 content, else -> errors
        for line in response.body.decode(response.encoding).splitlines():
            line = line.strip()
            if line: # get rid of empty lines
                #print line,
                if re.search('\<h1 class\=\"title\"\>',line):
                    flag = 1
                if re.search('<div class=\"region region-sidebar-first column sidebar\">',line):
                    flag = 0
                #interesting content
                if flag:
                    # make sure the stripper object doesn't strip the escaped html string (&...)
                    line = parser.unescape(line)
                    stripper.feed(line)
        # now get rif of remaining blank lines created by removing the html tags
        final_list = list()
        for e in stripper.get_data():
            e = e.strip()
            if e:
                final_list.append(e)
        return job_offer.JobOffer.from_job_string_list(final_list, response.url).to_dict()


class HTMLStripper(HTMLParser):
    '''
        see http://stackoverflow.com/a/925630
    '''
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return self.fed
