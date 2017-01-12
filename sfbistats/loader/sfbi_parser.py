# coding=utf-8

import os
import email
from pprint import pprint
import re
import mailbox
from collections import Counter

class EmlParser(object):

    def __init__(self, mails, stats):
        self.mails = mails
        self.stats = stats

    @classmethod
    def from_maildir(cls, mail_directory):
        """
        check encodings, categorize mails, and try to correct encodings problems
        """

        # keep tabs on some encoding related stuff
        stats = EmlParser.init_stats()

        # categories of mails
        # filename-> encoding, category
        mails = dict()

        weirderList = list()

        emlList = os.listdir(mail_directory)
        for filename in emlList:
            print(">>> " + filename)
            try:
                f = open(os.path.join(mail_directory, filename), 'r', encoding='utf-8')
            except:
                print ("Could not open "+filename+" in " + mail_directory)
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

            mail_dict['category'] = EmlParser.__categorize_mail(text)
            # keep some stats
            charset = mail_dict['encoding']
            EmlParser.update_stats(stats, charset, mail_dict['category'])

        pprint(stats)
        return cls(mails, stats)

    @classmethod
    def from_mbox(cls, file):

        # keep tabs on some encoding related stuff
        stats = EmlParser.init_stats()

        mails = dict()

        mbox = mailbox.mbox(file)
        for key, msg in mbox.items():
            try:
                charset, text = EmlParser.get_one_charset_payload(msg)
            except:#case where charset is None, broken stuff
                continue
            try:
                text = text.decode(charset, errors='replace')
            except:
                text = text.decode('latin1', errors='replace')
            mail_dict = dict()
            mails[key] = mail_dict
            mail_dict['email_text'] = text
            mail_dict['category'] = EmlParser.__categorize_mail(text)
            EmlParser.update_stats(stats, charset, mail_dict['category'])

        pprint(stats)
        return cls(mails, stats)

    def __categorize_mail(mail_text):
        #first determine if mail is recent and formatted, or ancient and anarchic
        flags = dict.fromkeys(["f1", "f2", "f3", "f4", "f5", "f6"], 0)
        for line in mail_text.splitlines(True):
            #print (">"+line)
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
            return 'formatted'
        elif flagsum == 0:
            return 'anarchic'
        else:
            return 'weird'

    def __extract_link(self, content):
        """
            given the content of a recent job mail, return the link to the sfbi website
        """
        flag = 0
        link = ''
        for line in content.splitlines():
            # in rare cases link is on the same line
            m = re.search('Voir la description complète du poste sur (http:\/\/(www.)?sfbi.fr(\S+))', line)
            if m is not None :
                flag = 1
                link = m.group(1)
                break
            if re.match('Voir la description complète du poste sur', line):
                flag = 1
            if re.match('^http:\/\/(www.)?sfbi.fr(\S+)', line):
                link = line
                break
        if flag:
            return link
        else:
            return None

    def get_link_list(self):
        link_list = list()
        for filename, dic in self.mails.items():
            if dic['category'] == 'formatted':
                text = dic['email_text']
                http_link = self.__extract_link(text)
                link_list.append(http_link)
        # there are duplicate mails, that give undesired duplicated links in the final list.
        uniq = Counter(link_list)
        uniq_link_list = list(uniq)
        return uniq_link_list

    @staticmethod
    def get_one_charset_payload(msg):
        """
        Returns one charset and payload from a mail, multipart or not.
        Takes the first charset that is defined in a mutlipart message, and returns this part's payload
        Charset can be None in some weird case that should be dismissed.
        Parameters
        ----------
        msg: email.message

        Returns
        -------
        string: charset of mail
        string: payload

        """
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_charset() is not None:
                    return part.get_content_charset(), part.get_payload(decode=True)

        else:
            if msg.get_content_charset() is None:
                raise ValueError('Charset is None, message too weird.')
            return msg.get_content_charset(), msg.get_payload(decode=True)

    @staticmethod
    def init_stats():
        stats = dict()
        stats['format'] = dict()
        stats['format']['recent_job_count'] = 0
        stats['format']['anarchic_count'] = 0
        stats['format']['recent_weird_count'] = 0
        stats['format']['corrected_count'] = 0
        stats['format']['recent_job_encoding'] = Counter()
        stats['format']['anarchic_encoding'] = Counter()
        stats['format']['recent_weird_encoding'] = Counter()
        stats['format']['corrected_count_from_charset'] = Counter()

        return stats

    @staticmethod
    def update_stats(stats, charset, category):
        if category == 'formatted':
            stats['format']['recent_job_count'] += 1
            stats['format']['recent_job_encoding'].update([charset])
        elif category == 'anarchic':
            stats['format']['anarchic_count'] += 1
            stats['format']['anarchic_encoding'].update([charset])
        else:
            # could be corrected with:
            # text = text.decode('latin1').encode('utf8')
            stats['format']['recent_weird_count'] += 1
            stats['format']['recent_weird_encoding'].update([charset])