# coding=utf-8

import os
import email
from pprint import pprint
import re

class EmlParser(object):

    def __init__(self, mail_directory):
        """
        check encodings, categorize mails, and try to correct encodings problems
        """
        print mail_directory

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


        # categories of mails
        # filename-> encoding, category
        mails = dict()


        weirderList = list()

        emlList = os.listdir(mail_directory)
        for filename in emlList:
            print ">>> " + filename
            try:
                f = open(os.path.join(mail_directory, filename), 'r')
            except:
                print "Could not open "+filename+" in " + mail_directory
                continue

            msg = email.message_from_file(f)
            mail_dict = dict()
            mails[filename] = mail_dict
            # determine original encoding of the message
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_charset() != None:
                        text = part.get_payload()
                        charset = part.get_content_charset()
                        break
            else:
                text = msg.get_payload()
                charset = str(msg.get_charsets()[0])
            mail_dict['email_text'] = text
            mail_dict['original_encoding'] = charset
            mail_dict['encoding'] = charset

            self.__categorize_mail(mail_dict)
            # keep some stats
            charset = mail_dict['encoding']
            if mail_dict['category'] == 'formatted':
                stats['format']['recent_job_count']+=1
                if charset in stats['format']['recent_job_encoding']:
                    stats['format']['recent_job_encoding'][charset] += 1
                else:
                    stats['format']['recent_job_encoding'][charset] = 1
            elif mail_dict['category'] == 'anarchic':
                stats['format']['anarchic_count'] += 1
                if charset in stats['format']['anarchic_encoding']:
                    stats['format']['anarchic_encoding'][charset] += 1
                else:
                    stats['format']['anarchic_encoding'][charset] = 1
            else:
                stats['format']['recent_weird_count'] += 1
                if charset in stats['format']['recent_weird_encoding']:
                    stats['format']['recent_weird_encoding'][charset] += 1
                else:
                    stats['format']['recent_weird_encoding'][charset] = 1


        self.stats = stats
        self.mails = mails
        pprint(stats)

    def __categorize_mail(self, mail_dict):
        text = mail_dict['email_text']

        #first determine if mail is recent and formatted, or ancient and anarchic
        flags = dict.fromkeys(["f1", "f2", "f3", "f4", "f5", "f6"], 0)
        for line in text.splitlines(True):
            #print ">"+line
            if re.match('^Type de poste : ', line):
                flags["f1"] = 1
            if re.match('^Intitulé du poste : ', line):
                flags["f2"] = 1
            if re.match('^Ville : ', line):
                flags["f3"] = 1
            if re.match('^Nom du contact : ', line):
                flags["f4"] = 1
            if re.match('^Email du contact : ', line):
                flags["f5"] = 1
            if re.match('^Voir la description complète du poste sur', line):
                flags["f6"] = 1

        # flagsum will be used as a measure of weirdness. It should be 6 for correctly formatted mails.
        flagsum = flags["f1"]+ flags["f2"]+ flags["f3"]+ flags["f4"]+ flags["f5"]+ flags["f6"]

        if flagsum == 6:
            mail_dict['category'] = 'formatted'
        elif flagsum == 0:
            mail_dict['category'] = 'anarchic'
        else:
            mail_dict['category'] = 'weird'

        #pprint(mail_dict)

    def __extract_link(self, content):
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

    def get_link_list(self):
        link_list = list()
        for filename, dic in self.mails.iteritems():
            if dic['category'] == 'formatted':
                text = dic['email_text']
                http_link = self.__extract_link(text)
                link_list.append(http_link)
        return link_list


