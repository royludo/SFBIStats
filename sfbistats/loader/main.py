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

db_name = 'sfbi_jobs'
mongo_client = pymongo.MongoClient()
sfbi_db = mongo_client[db_name]
job_collection = sfbi_db['jobs']

'''
    see http://stackoverflow.com/a/925630
'''
class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return self.fed


class MongoDBStorage(object):
    def process_item(self, item, spider):
        #job_collection.insert_one(item)
        print "mongo-> "+str(item)
        return item

'''
Une nouvelle offre d'emploi vient d'être postée sur le site www.sfbi.fr

Type de poste : Post-doc / IR
Intitulé du poste : Ingénieur coordination bioinformatique - France
Génomique (réf FGCOOR1)
Ville : Castanet-Tolosan (prox. Toulouse)
Nom du contact : Denis Milan
Email du contact : get-plage.rh@genotoul.fr

Voir la description complète du poste sur
http://www.sfbi.fr/content/ing%C3%A9nieur-coordination-bioinformatique-france-g%C3%A9nomique-r%C3%A9f-fgcoor1
'''


def extract_link(content):
    """
        given the content of a recent job mail, return the link to the sfbi website
    """
    flag = 0
    link = ''
    for line in content.splitlines():
        if re.match('Voir la description complète du poste sur', line):
            flag = 1
        if re.match('^http:\/\/(www.)?sfbi.fr', line):
            link = line
    if flag:
        return link
    else:
        return None

'''
    given a link to sfbi job page, get html and return the interesting job section
'''
def get_html_job_info(link):
    page = urllib2.urlopen(link)
    if page.getcode()==200:
        # correctly decode utf-8
        encoding = page.headers.getparam('charset')
        page = page.read().decode(encoding)
        text_list = parse_html(page)
    else:
        print "XXXXXXXXXXXXXXXXXXX HTTP ERROR " + page.getcode()

    return text_list

'''
    given html code, get the interesting section
'''
def parse_html(html):
    flag = 0
    parser = HTMLParser()
    stripper = HTMLStripper()
    for line in html.splitlines():
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
    return final_list



'''
    clean mongodb stuff
'''
def clear_db(client):
    print "Start cleaning DB"
    client.drop_database(db_name)
    print "DB " + db_name + " now clean"





mailDirectory = "/home/ludovic/Programs/Projects/SFBIStats/asset/mails"
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

exit(1)

# keep tabs on some encoding related stuff
stats = dict()
stats['format'] = dict()
stats['format']['recent_job_count'] = 0
stats['format']['anarchic_count'] = 0
stats['format']['recent_weird_count'] = 0
stats['format']['corrected_count'] = 0
stats['format']['recent_job_encoding'] = dict()
stats['format']['anarchic_encoding'] = dict()
stats['format']['recent_weird_encoding'] = dict()
stats['format']['corrected_count_from_charset'] = dict()

weirderList = list()

emlList = os.listdir(mailDirectory)
for filename in emlList:

    #print ">>> " + filename
    try:
        #f = codecs.open(mailDirectory+"\\"+filename,'r')
        f = open(mailDirectory+"/"+filename,'r')
    except:
        print "PB!! "+filename
        continue

    msg = email.message_from_file(f)
    if msg.is_multipart():
        for part in msg.walk():
            #print part.get_content_charset()
            if part.get_content_charset() != None:
                charset = part.get_content_charset()
                text = part.get_payload()
                break
    else:
        text = msg.get_payload()
        charset = str(msg.get_charsets()[0])


    #print msg.get_charset()
    #print msg.get_content_type()
    #print msg.get_content_charset()




    #text = f.read();
    #text = text.encode("utf-8")
    #guessed_encoding =  ftfy.guess_bytes(text)[1]
    #text = text.decode('latin-1').encode('utf-8')

    '''if guessed_encoding != 'utf-8':
        #print text
        text = text.decode('latin-1')#.encode('utf-8')
        #text = ftfy.fix_text(text)
        #print text
        #break;'''



    '''if filename == '7EE561A7-0000096E.eml':
        f = codecs.open(mailDirectory+"\\"+filename,'r','latin-1')
        text = f.read();
        print text
        #text = text.encode("latin-1")
        #print text
        text = text.encode("utf-8")
        print text
        #print ftfy.fix_text(text)
        break;
    else:
        continue'''

    '''if filename == '7EE561A7-0000096E.eml':
        #print f.read();
        print ftfy.fix_text(f.read())
    else:
        continue;
    break;'''

    #first determine if mail is recent and formatted, or ancient and anarchic
    flags = dict.fromkeys(["f1", "f2", "f3", "f4", "f5", "f6"], 0)
    for line in text.splitlines(True):
        #print ">"+line
        if re.match('^Type de poste : ',line):
            flags["f1"] = 1
        if re.match('^Intitulé du poste : ',line):
            flags["f2"] = 1
        if re.match('^Ville : ',line):
            flags["f3"] = 1
        if re.match('^Nom du contact : ',line):
            flags["f4"] = 1
        if re.match('^Email du contact : ',line):
            flags["f5"] = 1
        if re.match('^Voir la description complète du poste sur',line):
            flags["f6"] = 1
        '''m = re.search('charset=(.+?)\s',line)
        if m:
            charset = m.group(1)
            #clean the charset string which might look like 'utf-8;' 'UTF-8' or '"UTF-8";'
            charset = charset.upper()
            charset = charset.strip(';"')'''

    flagsum = flags["f1"]+ flags["f2"]+ flags["f3"]+ flags["f4"]+ flags["f5"]+ flags["f6"]
    if flagsum == 6:
        print filename + " recent "+ charset
        stats['format']['recent_job_count']+=1
        if charset in stats['format']['recent_job_encoding']:
            stats['format']['recent_job_encoding'][charset] +=1
        else:
            stats['format']['recent_job_encoding'][charset] = 1
        http_link = extract_link(text)
        print "Extracted link from mail: "+ http_link


        try:
            job_string_list = get_html_job_info(http_link)
        except:
            print "XXXXXXXXXXXXXXXXXX Could not get html page!!"
            continue
        announce = job_offer.JobOffer(job_string_list, http_link)
        print announce

        job_collection.insert_one(announce.to_dict())
        #break # ---------------- just one for test




    elif flagsum == 0:
        print filename + " ancient " + charset
        stats['format']['anarchic_count']+=1
        if charset in stats['format']['anarchic_encoding']:
            stats['format']['anarchic_encoding'][charset] +=1
        else:
            stats['format']['anarchic_encoding'][charset] = 1

        #we try to clean things by changing encoding
        if charset == "ISO-8859-1" or charset == "WINDOWS-1252":
            text = text.decode('latin1').encode('utf8')
        #elif charset == "WINDOWS-1252":

        #elif charset == "US-ASCII":

    else:
        print filename + " >>>>>>>>>>>> weird! "+ charset
        f.seek(0)
        #print(f.read())
        stats['format']['recent_weird_count']+=1
        if charset in stats['format']['recent_weird_encoding']:
            stats['format']['recent_weird_encoding'][charset] +=1
        else:
            stats['format']['recent_weird_encoding'][charset] = 1

        # now we correct the encoding to try to get back the mail correctly
        #print text
        text = text.decode('latin1').encode('utf8')
        #print text
        weirderFlag = 1;
        for line in text.splitlines(True):
            #print ">"+line
            if re.match('^Intitulé du poste : ',line):
                weirderFlag = 0;
                stats['format']['corrected_count']+=1
                if charset in stats['format']['corrected_count_from_charset']:
                    stats['format']['corrected_count_from_charset'][charset] +=1;
                else:
                    stats['format']['corrected_count_from_charset'][charset] = 1;
        if weirderFlag:
            # at this point a mail can fall in this ultimate category for 2 reasons:
            # - there's still encoding problems (é -> =E9 O.o)
            # - its format looks like the automatic sfbi one, but it's been hand made so 1 or 2 pattern match (like only Type de poste)
            print filename+" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<< WEIRDER!!!!!!!!!!!!!!!!!!!!!!!!! flagsum " + str(flagsum)
            weirderList.append(filename)






pprint.pprint(stats['format'])
pprint.pprint(weirderList)


#clear_db(mongo_client)
