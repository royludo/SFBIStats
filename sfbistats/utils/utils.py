# -*- coding: utf-8 -*-
""" Utilities

Miscellaneous stuff.

"""
from __future__ import print_function, unicode_literals, division
import re
import geopy
import numpy as np
import csv
import pkg_resources
import collections
import json
from bson import json_util

from ..job_offer import JobOfferAnon

def load_from_json(file):
    """
    This function load a json database into a list of dict.

    Parameters
    ----------
    file : file handler
        An already opened json file handler to the serialized job list.

    Returns
    -------
    list

    """
    job_list = list()
    city_dict = collections.defaultdict(int)
    for l in file.readlines():
        # use dict instead of directly object, better with pandas
        job = JobOfferAnon.from_json(json.loads(l, object_hook=json_util.object_hook)).to_dict()
        job['city'] = sanitize_city_name(job['city'])
        job['city'] = sanitize_city_name_for_geoloc(job['city'])
        city_file = pkg_resources.resource_filename('sfbistats.utils', 'city_locations.csv')
        dep, reg = city_to_dep_region(job['city'], city_file)
        job['department'] = dep
        job['region'] = reg
        job['duration'] = sanitize_duration(job['duration'])
        city_dict[job['city']] += 1
        job_list.append(job)
    job_list = spell_correct(job_list, city_dict)
    return job_list

def sanitize_city_name(orig_name):
    """
    Ensure that city names only have words, with no -, upper first letters, with ' and /
    (ex: Villefranche/Mer, Villeneuve D'Ascq)
    All numbers initially present are removed, except when it's the only characters.
    Ensure that words are separated by 1 space only

    Will correct these:
        MontréAl -> Montréal
        Gif-Sur-Yvette -> Gif Sur Yvette
        Gif-Sur-Yvette, France -> Gif Sur Yvette
        Chappes (63) -> Chappes
        91000 Evry -> Evry
        Hinxton   Cambridge -> Hinxton Cambridge

    Will leave things like this:
        Evry Puis Saclay En 2015 -> Evry Puis Saclay En
        Rennes Ou Toulouse -> Rennes Ou Toulouse
        Paris/Ivry Sur Seine -> Paris/Ivry Sur Seine

    Parameters
    ----------
    orig_name : string

    Returns
    -------
    string

    """
    m = re.match('\d*\s*(\w+[^,\(\)\d]+)[,\(\)\d]?', orig_name, re.UNICODE)
    if not m:
        name = orig_name
    else:
        name =  m.group(1).strip().replace('-', ' ').title()
    # remove multiple spaces
    name = re.sub('\s+', ' ', name)
    return name

def sanitize_city_name_for_geoloc(orig_name):
    """
    Ensure that city names can be recognized by GoogleV3 API.

    Parameters
    ----------
    orig_name : string

    Returns
    -------
    string

    """
    orig_name = orig_name
    # A dictionary of substitutions
    replace_dict = {'ou': '|', 'or': '|', 'et': '|', 'and': '|', 'puis': '|',
                    '/mer': ' Sur Mer',
                    'cedex': '',
                    'plateau de saclay': 'Saclay',
                    'ile de france': 'Paris',
                    'france': 'Paris',
                    'montpelllier': 'Montpellier',
                    'cambridege': 'Cambridge',
                    'evry orsay': 'Evry',
                    'lyon evry': 'Lyon',
                    'marseille nice': 'Marseille',
                    'lyon villeurbanne': 'Lyon',
                    'clermont fd': 'Clermont Ferrand',
                    'hinxton cambridge': 'Hinxton',
                    'hinxton cambridge uk': 'Hinxton',
                    'bordeaux cestas': 'Bordeaux',
                    'montpellier perpignan': 'Montpellier',
                    'nice sophia antipolis': 'Nice'}
    pattern = r'\b({})\b'.format('|'.join(sorted(re.escape(k) for k in replace_dict)))
    name = re.sub(pattern, lambda m: replace_dict.get(m.group(0).lower()), orig_name, flags=re.IGNORECASE)
    # not in the regex because of accents
    name = name.replace(u'Université Paris Saclay', 'Saclay')
    name = name.replace(u"Génopôle D'Evry", 'Evry')
    name = name.replace(u'Île De', 'Paris')
    name = name.replace(u' Paris Région Parisienne', 'Paris')
    name = name.replace(u'Région Parisienne', 'Paris')
    name = re.sub('(\s?Paris\s?)+', 'Paris', name)
    # When several cities, just keep the first one
    name = name.replace('/', '|').split('|')[0]
    name = name.strip()

    return name


def sanitize_duration(job_duration_string):
    """
    convert anarchic duration string (ex: 24 mois, 1.5 années, 18 à 24 mois...) to int
    unit returned is in months
    when several numbers are present, the first (=the minimum) is returned
    if just a number and nothing else, we'll consider it as months
    return -1 if can't parse correctly
    return 0 if not applicable (ex: CDI)
    """
    m1 = re.search('(\d+).*(mois|month|months).*', job_duration_string)
    m2 = re.search('(\d+).*(année|années|an|ans|year|years).*', job_duration_string)
    m3 = re.search('(\d+).*(semaine|semaines|week|weeks).*', job_duration_string)
    m4 = re.search('(\d+)', job_duration_string.lower())

    m5 = re.search('(indéterminé|indeterminé|indetermine|cdi|inderterminé|full time)', job_duration_string.lower())

    if m1:
        dur = int(m1.group(1))
    elif m2:
        dur = int(m2.group(1)) * 12
    elif m3:
        dur = int(m3.group(1)) / 4
    elif m4:
        dur = int(m4.group(1))
    elif m5:
        dur = 0
    else:
        dur = -1
    return dur


def get_colors():
    """
    return colors used for all matplotlib charts
    because the colors for the plots defined in rcParams are used everywhere, in all plot functions,
    BUT NOT in pie charts -___-"
    and it's impossible to access pyplot's color cycler's list that we previously defined
    (see http://stackoverflow.com/questions/13831549/get-matplotlib-color-cycle-state)

    Returns
    -------
    list

    """
    return ['orange', 'burlywood', 'brown', 'cornflowerblue', 'crimson', 'darkolivegreen', 'silver', 'darkslategray',
          'plum', 'peru', 'saddlebrown', 'mediumorchid', 'goldenrod', 'darksage', 'coral', 'lightseagreen']


def query_GoogleV3(name):
    print('Querying for location:', name)
    service = geopy.GoogleV3(domain='maps.google.fr', timeout=5)
    loc = service.geocode(name, exactly_one=True)
    if loc is None:  # extreme case, google doesn't return anything
        # try to split and query separate terms
        names = name.split()
        if len(names) == 1:
            raise NameError(name, 'Could not get any result from google API')
        else:
            loc = service.geocode(names[0], exactly_one=True)
    address_dict = loc.raw['address_components']
    print(address_dict)
    d = dict()
    d['admin_lvl1'] = ''
    d['admin_lvl2'] = ''
    d['locality'] = ''
    d['colloquial'] = ''
    d['country'] = ''
    # first pass
    for component in address_dict:
        print(component['long_name'], ' ## ', component['types'])
        if u'administrative_area_level_2' in component['types']:
            d['admin_lvl2'] = component['long_name']
        elif u'colloquial_area' in component['types']:  # sometimes contains region name instead of lvl1
            d['colloquial'] = component['long_name']
        elif u'administrative_area_level_1' in component['types']:
            d['admin_lvl1'] = component['long_name']
        elif u'country' in component['types']:
            d['country'] = component['long_name']
        elif u'locality' in component['types']:
            d['locality'] = component['long_name']
    return d


def city_to_dep_region(name, city_filename):
    """ Returns the department and region from the city name, if located in France.
    Otherwise, returns 'Étranger'. """

    city_dict = {}
    with open(city_filename, 'r', encoding='utf-8') as city_file:
        for l in csv.reader(city_file):
            #l = l.decode('utf-8')
            #l = map(lambda x: x.decode('utf8'), l)
            city, dep, reg = l
            city_dict[city] = (dep, reg)

    if name in city_dict:
        return city_dict[name]
    else:
        print('Unknown city:', name)
        loc_dic = query_GoogleV3(name)

        # check if everything is alright
        if not loc_dic['country'] or loc_dic['country'] != 'France':
            country = u'Étranger'
        else:
            country = loc_dic['country']
            if loc_dic['admin_lvl1']:
                reg = loc_dic['admin_lvl1']
            else:
                if loc_dic['colloquial']:
                    reg = loc_dic['colloquial']
                else:  # Cadarache case, search again
                    loc_dic2 = query_GoogleV3(loc_dic['locality'])
                    if loc_dic2['admin_lvl1']:
                        reg = loc_dic2['admin_lvl1']
                    else:
                        if loc_dic2['colloquial']:
                            reg = loc_dic2['colloquial']
                        else:
                            raise NameError(name, 'Could not find region')
            if loc_dic['admin_lvl2']:
                dep = loc_dic['admin_lvl2']
            else: # search again
                loc_dic2 = query_GoogleV3(loc_dic['locality'])
                if loc_dic2['admin_lvl2']:
                    reg = loc_dic2['admin_lvl2']
                else:
                    raise NameError(name, 'Could not find region')


        print ('Found:', ', '.join([dep, reg, country]))

        # Conversion to new regions
        conv_table = [(('haute normandie','basse normandie'), 'Normandie'),
                      (('champagne ardenne','alsace','lorraine', 'alsace champagne ardenne lorraine', 'grand est'), 'Grand-Est'),
                      (('bourgogne',u'franche comté', u'bourgogne franche comté'),u'Bourgogne-Franche-Comté'),
                      (('auvergne',u'rhône alpes', u'auvergne rhône alpes'),u'Auvergne-Rhône-Alpes'),
                      (('aquitaine','limousin','poitou charentes', 'aquitaine limousin poitou charentes', 'nouvelle aquitaine'), 'Nouvelle-Aquitaine'),
                      (('languedoc roussillon',u'midi pyrénées', u'languedoc roussillon midi pyrénées'), 'Occitanie'),
                      (('nord pas de calais','picardie','nord pas de calais picardie', 'hauts de france'), 'Hauts-de-France'),
                      (('pays de la loire'), 'Pays-de-la-Loire'),
                      (('centre'), 'Centre-Val-de-Loire'),
                      ((u'provence alpes côte d\'azur'), u'Provence-Alpes-Côte-d\'Azur'),
                      ((u'île de france', 'ile de france'), u'Île-de-France')]
        newregions_dict = {}
        for keylist in conv_table:
            newregions_dict.update(dict.fromkeys(keylist[0], keylist[1]))
        normalize_reg = reg.lower().replace('-', ' ')
        old_reg = reg
        if normalize_reg in newregions_dict:
            reg = newregions_dict[normalize_reg]
        print(old_reg+"     "+normalize_reg+"      "+reg)

        if country != 'France':
            dep = u'Étranger'
            reg = u'Étranger'
        line_list = [name, dep, reg]
        new_line = u','.join(line_list)
        with open(city_filename, 'a', encoding='utf-8') as city_file:
            print (new_line, file=city_file)
        return dep, reg


def levenshtein(source, target):
    """
    see https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    5th example

    Parameters
    ----------
    source
    target

    Returns
    -------

    """
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


def get_close_spelling(city, city_dict):
    leven_list = list()
    for city_check in city_dict.keys():
        dl = levenshtein(city, city_check)
        if (len(city) < 10 and dl == 1) or (len(city) > 10 and dl < 4 and dl != 0):
            leven_list.append(city_check)
    return leven_list


def spell_correct(job_list, city_dict):
    replace_dict = dict()
    for city in city_dict.keys():
        closests = get_close_spelling(city, city_dict)
        if len(closests) == 1:
            alt = closests[0]
            if alt in replace_dict.values():
                continue
            #print(alt.decode('utf8')+' '+str(city_dict[alt])+' '+city.decode('utf8')+' '+str(city_dict[city]))
            if city_dict[alt] > city_dict[city]:
                replace_dict[city] = alt
            else:
                replace_dict[alt] = city
    #print(replace_dict)
    for job in job_list:
        if job['city'] in replace_dict:
            job['city'] = replace_dict[job['city']]
    return job_list

