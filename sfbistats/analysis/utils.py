# -*- coding: utf-8 -*-
""" Utilities

Miscellaneous stuff.

"""

import re

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
        return orig_name
    else:
        return m.group(1).strip().replace('-', ' ').title()


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

    m5 = re.search('(indéterminé|indeterminé|indetermine|CDI)', job_duration_string.lower())

    if m1:
        return int(m1.group(1))
    if m2:
        return int(m2.group(1)) * 12
    if m3:
        return int(m3.group(1)) / 4
    if m4:
        return int(m4.group(1))
    if m5:
        return ''
    return '-1'


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

