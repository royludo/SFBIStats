# -*- coding: utf-8 -*-
""" Utilities

Miscellaneous stuff.

"""
from __future__ import print_function, unicode_literals
import re
import geopy

def sanitize_city_name(orig_name):
    """
    Ensure that city names only have words, with no -, upper first letters, with ' and /
    (ex: Villefranche/Mer, Villeneuve D'Ascq)
    All numbers initially present are removed, except when it's the only characters.

    Will correct these:
        MontréAl -> Montréal
        Gif-Sur-Yvette -> Gif Sur Yvette
        Gif-Sur-Yvette, France -> Gif Sur Yvette
        Chappes (63) -> Chappes
        91000 Evry -> Evry

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
                    'montpelllier': 'Montpellier',
                    'cambridege': 'Cambridge',
                    'evry   orsay': 'Evry',
                    'lyon   evry': 'Lyon',
                    'marseille   nice': 'Marseille',
                    'lyon villeurbanne': 'Lyon',
                    'clermont fd': 'Clermont Ferrand',
                    'bordeaux   cestas': 'Bordeaux'}
    pattern = r'\b({})\b'.format('|'.join(sorted(re.escape(k) for k in replace_dict)))
    name = re.sub(pattern, lambda m: replace_dict.get(m.group(0).lower()), orig_name, flags=re.IGNORECASE)
    # not in the regex because of accents
    name = name.replace(u'Université Paris Saclay', 'Saclay')
    name = name.replace(u"Génopôle D'Evry", 'Evry')
    name = name.replace(u'Île De', 'Paris')
    name = name.replace(u'   Paris   Région Parisienne', 'Paris')
    # When several cities, just keep the first one
    name = name.replace('/', '|').split('|')[0]

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

def city_to_dep_region(name, city_filename):
    """ Returns the department and region from the city name, if located in France.
    Otherwise, returns 'Étranger'. """

    name = name.decode('utf-8')
    city_dict = {}
    with open(city_filename, 'r') as city_file:
        city_file.readline()
        for l in city_file:
            l = l.decode('utf-8')
            city, dep, reg = l.strip().split(',')
            city_dict[city] = (dep, reg)

    if name in city_dict:
        return city_dict[name]
    else:
        print ('Unknown city:', name)
        service = geopy.GoogleV3(domain='maps.google.fr', timeout=5)
        loc = service.geocode(name, exactly_one=True)
        address_dict = loc.raw['address_components']
        for component in address_dict:
            if component['types'][0] == u'administrative_area_level_2':
                dep = component['long_name']
            elif component['types'][0] == u'administrative_area_level_1':
                reg = component['long_name']
            elif component['types'][0] == u'country':
                country = component['long_name']
        print ('Found:', ', '.join([dep, reg, country]))

        # Conversion to new regions
        conv_table = [(('Haute-Normandie','Basse-Normandie'), 'Normandie'),
                      (('Champagne-Ardenne','Alsace','Lorraine'), 'Alsace-Champagne-Ardenne-Lorraine'),
                      (('Bourgogne',u'Franche-Comté'),u'Bourgogne-Franche-Comté'),
                      (('Auvergne',u'Rhône-Alpes'),u'Auvergne-Rhône-Alpes'),
                      (('Aquitaine','Limousin','Poitou-Charentes'),'Aquitaine-Limousin-Poitou-Charentes'),
                      (('Languedoc-Roussillon',u'Midi-Pyrénées'),u'Languedoc-Roussillon-Midi-Pyrénées'),
                      (('Nord-Pas-de-Calais','Picardie'),'Nord-Pas-de-Calais-Picardie')]
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
