# -*- coding: utf-8 -*-
""" Utilities

Miscellaneous stuff.

"""
from __future__ import print_function, unicode_literals
import re
import geopy
import numpy as np
import csv
import pkg_resources
import collections
from bson import json_util
import json
import sfbistats.job_offer as sfbi_job

def load_from_json(file):
    """

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
        job = sfbi_job.JobOfferAnon.from_json(json.loads(l, object_hook=json_util.object_hook)).to_dict()
        job['city'] = sanitize_city_name(job['city'])
        job['city'] = sanitize_city_name_for_geoloc(job['city'])
        city_file = pkg_resources.resource_filename('sfbistats.analysis', 'city_locations.csv')
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
    return name.encode('utf-8')

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
    orig_name = orig_name.decode('utf-8')
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
                    'bordeaux cestas': 'Bordeaux'}
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

    return name.encode('utf-8') # don't forget to encode the output


def sanitize_duration(job_duration_string):
    """
    convert anarchic duration string (ex: 24 mois, 1.5 années, 18 à 24 mois...) to int
    unit returned is in months
    when several numbers are present, the first (=the minimum) is returned
    if just a number and nothing else, we'll consider it as months
    return -1 if can't parse correctly
    return nothing if not applicable (ex: CDI)
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
        dur = ''
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

    name = name.decode('utf-8')
    city_dict = {}
    with open(city_filename, 'r') as city_file:
        for l in csv.reader(city_file):
            #l = l.decode('utf-8')
            l = map(lambda x: x.decode('utf8'), l)
            city, dep, reg = l
            city_dict[city] = (dep, reg)

    if name in city_dict:
        return city_dict[name]
    else:
        print ('Unknown city:', name)
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
        conv_table = [(('Haute-Normandie','Basse-Normandie'), 'Normandie'),
                      (('Champagne-Ardenne','Alsace','Lorraine'), 'Alsace-Champagne-Ardenne-Lorraine'),
                      (('Bourgogne',u'Franche-Comté'),u'Bourgogne-Franche-Comté'),
                      (('Auvergne',u'Rhône-Alpes'),u'Auvergne-Rhône-Alpes'),
                      (('Aquitaine','Limousin','Poitou-Charentes'),'Aquitaine-Limousin-Poitou-Charentes'),
                      (('Languedoc-Roussillon',u'Midi-Pyrénées'),u'Languedoc-Roussillon-Midi-Pyrénées'),
                      (('Nord-Pas-de-Calais','Picardie'),'Nord-Pas-de-Calais-Picardie'),
                      (['Nord-Pas-de-Calais Picardie'],'Nord-Pas-de-Calais-Picardie')]
        newregions_dict = {}
        for keylist in conv_table:
            newregions_dict.update(dict.fromkeys(keylist[0], keylist[1]))
        if reg in newregions_dict:
            reg = newregions_dict[reg]

        if country != 'France':
            dep = u'Étranger'
            reg = u'Étranger'
        line_list = [name, dep, reg]
        new_line = u','.join(line_list)
        with open(city_filename, 'a') as city_file:
            print (new_line.encode('utf-8'), file=city_file)
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
    for city_check in city_dict.iterkeys():
        dl = levenshtein(city.decode('utf8'), city_check.decode('utf8'))
        if (len(city) < 10 and dl == 1) or (len(city) > 10 and dl < 4 and dl != 0):
            leven_list.append(city_check)
    return leven_list


def spell_correct(job_list, city_dict):
    replace_dict = dict()
    for city in city_dict.iterkeys():
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