# coding=utf-8
from __future__ import division, print_function
import re
import datetime


class JobOffer(object):
    def __init__(self):
        self.http_link = ''
        self.title = ''
        self.user = ''
        self.submission_date = None
        self.contract_type = ''
        self.contract_sub_type = ''
        self.duration = ''
        self.city = ''
        self.starting_date = None
        self.lab = ''
        self.contact_name = ''
        self.limit_date = None
        self.validity_date = None
        self.description = ''

    @staticmethod
    def from_json(json):
        """
        :param json:
        :return:
        """
        job = JobOffer()
        job.http_link = json['http_link']
        job.title = json['title']
        job.user = json['user']
        job.submission_date = json['submission_date'].date()
        job.contract_type = json['contract_type']
        job.contract_sub_type = json['contract_subtype']
        job.duration = json['duration']
        job.city = json['city']
        job.starting_date = json['starting_date']
        job.lab = json['lab']
        job.contact_name = json['contact_name']
        job.limit_date = json['limit_date']
        job.validity_date = json['validity_date']
        job.description = json['description']
        return job

    @staticmethod
    def from_mongodb(document):
        """
        :param document:
        :return:
        """
        print(document)

    @staticmethod
    def from_job_string_list(job_string_list, http_link):
        """
        :param job_string_list: list of all elements parsed from the html page, stripped from html markup
        :param http_link: the page's link
        """
        job = JobOffer()
        job.http_link = http_link
        # the mail initial object, job and announce title
        # ex: 'Bioinformatics developer', 'Working on annotation pipeline'...
        job.title = job_string_list[1]

        # the sfbi user who submitted the announce
        submission_string = job.seek_info('^Soumis par', job_string_list, 0)
        if not submission_string:
            raise Exception('User field not found!')
        m = re.search('Soumis par (.+) le .+(\d\d/\d\d/\d+)', submission_string)
        job.user = m.group(1)
        job.submission_date = datetime.datetime.strptime(m.group(2), '%d/%m/%Y')

        # from now on, the index can change.
        # CDD and CDI have subtypes, thus making the list longer by adding additional fields
        # stage and thèse don't have subtypes
        type = job.seek_info('Type de poste', job_string_list, 1)
        if type == 'Stage' or type == 'Thèse':
            job.contract_type = type
            job.contract_sub_type = ''
        else:
            job.contract_type = type
            job.contract_sub_type = job.seek_info('Type de poste', job_string_list, 3)

        # field Durée du poste may not be present for CDI. Some CDI have it, with indéterminée.
        # empty is not applicable (for CDI)
        duration_string = job.seek_info('Durée du poste', job_string_list, 1)
        if duration_string:
            job.duration = duration_string
        else:
            job.duration = ''

        city_string = job.seek_info('Ville', job_string_list, 1)
        if not city_string:
            raise Exception('Ville field not found!')
        job.city = city_string.title()

        starting_date_string = job.seek_info('Date de début', job_string_list, 1)
        if starting_date_string:
            m = re.search('(\d\d/\d\d/\d+)', starting_date_string)
            job.starting_date = datetime.datetime.strptime(m.group(1), '%d/%m/%Y')
        else:
            job.starting_date = ''

        lab_string = job.seek_info('Laboratoire', job_string_list, 1)
        if lab_string:
            job.lab = lab_string.title()
        else:
            job.lab = ''

        contact_name_string = job.seek_info('Nom et prénom du contact', job_string_list, 1)
        if not contact_name_string:
            raise Exception('Nom du contact field not found!')
        job.contact_name = contact_name_string.title()

        limit_date_string = job.seek_info('Date limite de candidature', job_string_list, 1)
        if limit_date_string:
            m = re.search('(\d\d/\d\d/\d+)', limit_date_string)
            job.limit_date = datetime.datetime.strptime(m.group(1), '%d/%m/%Y')
        else:
            job.limit_date = ''

        validity_date_string = job.seek_info('Date de validité', job_string_list, 1)
        if validity_date_string:
            m = re.search('(\d\d/\d\d/\d+)', validity_date_string)
            job.validity_date = datetime.datetime.strptime(m.group(1), '%d/%m/%Y')
        else:
            job.validity_date = ''

        job.description = job.get_full_description(job_string_list)
        return job

    def __str__(self):
        return (">>title: " + self.title +
                "\n- user: " + self.user +
                "\n- submission date: " + str(self.submission_date) +
                "\n- contract type: " + self.contract_type +
                "\n- contract subtype: " + self.contract_sub_type +
                "\n- duration: " + str(self.duration) +
                "\n- city: " + self.city +
                "\n- starting date: " + str(self.starting_date) +
                "\n- lab: " + self.lab +
                "\n- contact name: " + self.contact_name +
                "\n- limit date: " + str(self.limit_date) +
                "\n- validity date: " + str(self.validity_date) +
                "\n- description: " + self.description +
                "\n- http link: " + self.http_link
                )

    def to_dict(self):
        return {"title": self.title,
                "user": self.user,
                "submission_date": self.submission_date,
                "contract_type": self.contract_type,
                "contract_subtype": self.contract_sub_type,
                "duration": self.duration,
                "city": self.city,
                "starting_date": self.starting_date,
                "lab": self.lab,
                "contact_name": self.contact_name,
                "limit_date": self.limit_date,
                "validity_date": self.validity_date,
                "description": self.description,
                "http_link": self.http_link
                }

    @staticmethod
    def seek_info(pattern, job_string_list, offset):
        """
        look for pattern in the job_string_list
        then returns the element located at pattern position + offset
        ex: if offset = 1, return element next to pattern
        """
        i = 0
        for e in job_string_list:
            m_desc = re.match('Description du poste:', e)
            # we arrived at the Description anarchic field, the rest doesn't interest us
            if m_desc:
                return None

            m = re.match(pattern, e)
            if m and i != len(job_string_list) + 1:
                return job_string_list[i + offset]
            i += 1
        return None

    @staticmethod
    def get_full_description(job_string_list):
        """
        description field is long, and full of html markup, so it spans several elements of the list.
        the function basically take everything remaining in the job_string_list
        """
        flag = 0
        result = ''
        for e in job_string_list:
            m = re.match('Description', e)
            if m:
                flag = 1
                continue
            if flag == 1:
                result += e
        return result


class JobOfferAnon(object):
    """
    Same as JobOffer but less fields to make the data anonymous

    from mongodb:
    mongoexport --db sfbi_jobs --collection jobs --out jobs_anon.json
    --fields submission_date,contract_type,city,title,limit_date,starting_date,contract_subtype,validity_date,duration
    """
    def __init__(self):
        self.title = ''
        self.submission_date = None
        self.contract_type = ''
        self.contract_sub_type = ''
        self.duration = ''
        self.city = ''
        self.starting_date = None
        self.limit_date = None
        self.validity_date = None

    @staticmethod
    def from_json(json):
        """
        :param json:
        :return:
        """
        job = JobOfferAnon()
        job.title = json['title']
        job.submission_date = json['submission_date'].date()
        job.contract_type = json['contract_type']
        job.contract_sub_type = json['contract_subtype']
        job.duration = json['duration']
        job.city = json['city']
        job.starting_date = json['starting_date']
        job.limit_date = json['limit_date']
        job.validity_date = json['validity_date']
        return job

    @staticmethod
    def from_JobOffer(normal_job):
        jobAnon = JobOfferAnon()
        jobAnon.title = normal_job.title
        jobAnon.submission_date = normal_job.submission_date
        jobAnon.contract_type = normal_job.contract_type
        jobAnon.contract_sub_type = normal_job.contract_sub_type
        jobAnon.duration = normal_job.duration
        jobAnon.city = normal_job.city
        jobAnon.starting_date = normal_job.starting_date
        jobAnon.limit_date = normal_job.limit_date
        jobAnon.validity_date = normal_job.validity_date
        return jobAnon

    def to_dict(self):
        return {"title": self.title,
                "submission_date": self.submission_date,
                "contract_type": self.contract_type,
                "contract_subtype": self.contract_sub_type,
                "duration": self.duration,
                "city": self.city,
                "starting_date": self.starting_date,
                "limit_date": self.limit_date,
                "validity_date": self.validity_date,
                }

