# -*- coding: utf-8 -*-
""" Maps

Display city aggregated data.

"""

import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import geopy
import re
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
import math
import sfbistats.analysis.utils as sfbi_utils
import os


def init_france_map():
    # map coordinates
    llcrnrlon = -5.2
    llcrnrlat = 42
    urcrnrlon = 9
    urcrnrlat = 52.5

    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111)
    fr_map = Basemap(projection='tmerc', resolution='l', area_thresh=1000, epsg=2192,
                     llcrnrlon=llcrnrlon,
                     llcrnrlat=llcrnrlat,
                     urcrnrlon=urcrnrlon,
                     urcrnrlat=urcrnrlat)
    fr_map.drawcoastlines()
    fr_map.drawcountries()
    return fig, ax, fr_map


def draw_pie(ax, ratios, X=0, Y=0, size=100):
    xy = []
    start = 0.
    for ratio in ratios:
        x = [0] + np.cos(np.linspace(2 * math.pi * start, 2 * math.pi * (start + ratio), 30)).tolist()
        y = [0] + np.sin(np.linspace(2 * math.pi * start, 2 * math.pi * (start + ratio), 30)).tolist()
        xy1 = zip(x, y)
        xy.append(xy1)
        start += ratio

    for i, xyi in enumerate(xy):
        ax.scatter([X], [Y], marker=(xyi, 0), s=size, facecolor=sfbi_utils.get_colors()[i])


def get_contract_type_ratios(city_dict):
    l = list()
    for type in city_dict['type_count']:
        l.append(city_dict['type_count'][type] / city_dict['count'])
    return l


def get_contract_subtype_ratios(city_dict):
    l = list()
    for type in city_dict['subtype_count']:
        l.append(city_dict['subtype_count'][type] / city_dict['subtype_total'])
    return l


def run(job_list, output_dir):

    print "Running maps.py"
    service = geopy.Nominatim(timeout=5)  # country_bias='FR',

    df = pd.DataFrame(job_list, columns=['city', 'submission_date', 'contract_type', 'contract_subtype', 'duration'])

    '''
        city treatment part
        Ile-de-France is treated specially, aggregated for better visibility on national map
        and displayed as zoomed region
    '''
    print " Getting geolocation of cities from Nominatim web service"
    df_city = pd.DataFrame(pd.Series(df.city).value_counts().head(30))
    location_dict = dict()
    IDF_total_count = 0
    for city, s in df_city.iterrows():
        #print city + " " + str(s[0])
        city = city
        count = s[0]
        if location_dict.has_key(city):
            location_dict[city]['count'] += count
        else:
            location_dict[city] = dict()
            location_dict[city]['count'] = count
            loc = service.geocode(city, exactly_one=True)
            #print loc.address
            location_dict[city]['longitude'] = loc.longitude
            location_dict[city]['latitude'] = loc.latitude
            if re.search('Île-de-France', loc.address.encode('utf8')):
                location_dict[city]['isinIDF'] = True
                IDF_total_count += count
            else:
                location_dict[city]['isinIDF'] = False
    # add the IDF special case
    location_dict['IDF'] = dict()
    location_dict['IDF']['count'] = IDF_total_count
    IDFloc = service.geocode('Paris', exactly_one=True)
    location_dict['IDF']['longitude'] = IDFloc.longitude
    location_dict['IDF']['latitude'] = IDFloc.latitude
    location_dict['IDF']['isinIDF'] = False

    df4 = pd.DataFrame({'city': df.city, 'type': df.contract_type}).reset_index(). \
        groupby(['city', 'type'])['index'].count().reset_index(name='count')
    df4_t = df4.pivot(index='city', columns='type', values='count').fillna(0)
    location_dict['IDF']['type_count'] = dict()
    for e in df4_t.iterrows():
        city = e[0]
        if city in location_dict:
            location_dict[city]['type_count'] = dict()
            for c in list(df4_t.columns.values):
                location_dict[city]['type_count'][c] = e[1][c]
                if location_dict[city]['isinIDF']:
                    if not c in location_dict['IDF']['type_count']:
                        location_dict['IDF']['type_count'][c] = e[1][c]
                    else:
                        location_dict['IDF']['type_count'][c] += e[1][c]

    df5 = pd.DataFrame({'city': df.city, 'subtype': df.contract_subtype}).reset_index(). \
        groupby(['city', 'subtype'])['index'].count().reset_index(name='count')
    df5_t = df5.pivot(index='city', columns='subtype', values='count').fillna(0)
    location_dict['IDF']['subtype_count'] = dict()
    location_dict['IDF']['subtype_total'] = 0
    for e in df5_t.iterrows():
        city = e[0]
        if city in location_dict:
            location_dict[city]['subtype_count'] = dict()
            location_dict[city]['subtype_total'] = 0
            for c in list(df5_t.columns.values):
                # skip empty subtype corresponding to stage and thesis
                if c:
                    location_dict[city]['subtype_count'][c] = e[1][c]
                    location_dict[city]['subtype_total'] += e[1][c]
                    if location_dict[city]['isinIDF']:
                        if not c in location_dict['IDF']['subtype_count']:
                            location_dict['IDF']['subtype_count'][c] = e[1][c]
                        else:
                            location_dict['IDF']['subtype_count'][c] += e[1][c]
                        location_dict['IDF']['subtype_total'] += e[1][c]

    '''
        drawing part
    '''
    print " Drawing maps"
    fig, ax, fr_map = init_france_map()

    for city in location_dict.iterkeys():
        if not location_dict[city]['isinIDF']:
            # print city+" "+str(location_dict[city]['count'])
            x, y = fr_map(location_dict[city]['longitude'], location_dict[city]['latitude'])
            fr_map.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count'] / 2), alpha=0.5)
            plt.text(x + location_dict[city]['count'] * 320, y + location_dict[city]['count'] * 320, city.decode('utf8'))

    axins = zoomed_inset_axes(ax, 3.5, loc=3)
    # NE 49.241299, 3.55852
    # SW 48.120319, 1.4467
    axins.set_xlim(fr_map(location_dict['IDF']['longitude'] - 0.8, location_dict['IDF']['longitude'] + 0.8))
    axins.set_ylim(fr_map(location_dict['IDF']['latitude'] - 0.3, location_dict['IDF']['latitude'] + 0.3))

    map2 = Basemap(projection='tmerc', resolution='l', area_thresh=1000,
                   llcrnrlon=location_dict['IDF']['longitude'] - 0.8, llcrnrlat=location_dict['IDF']['latitude'] - 0.3,
                   urcrnrlon=location_dict['IDF']['longitude'] + 0.8, urcrnrlat=location_dict['IDF']['latitude'] + 0.3,
                   epsg=2192, ax=axins)
    map2.drawmapboundary()

    for city in location_dict.iterkeys():
        if location_dict[city]['isinIDF']:
            #print city + " " + str(location_dict[city]['count'])
            x, y = map2(location_dict[city]['longitude'], location_dict[city]['latitude'])
            map2.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count'] / 2), alpha=0.5)
            plt.text(x + location_dict[city]['count'] * 85, y + location_dict[city]['count'] * 85, city, va='bottom')

    plt.savefig(os.path.join(output_dir, 'figure_4_1.svg'), bbox_inches='tight')
    plt.close()

    ########################
    fig, ax, fr_map = init_france_map()

    for city in location_dict.iterkeys():
        if not location_dict[city]['isinIDF']:
            #print city + " " + str(location_dict[city]['count'])
            x, y = fr_map(location_dict[city]['longitude'], location_dict[city]['latitude'])
            ratio_list = get_contract_type_ratios(location_dict[city])
            draw_pie(ax, ratios=ratio_list, X=x, Y=y, size=600)
            # map_contract_type.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count']/2), alpha=0.5)
            plt.text(x, y, city.decode('utf8'))

    axins = zoomed_inset_axes(ax, 3.5, loc=3)
    # NE 49.241299, 3.55852
    # SW 48.120319, 1.4467
    axins.set_xlim(fr_map(location_dict['IDF']['longitude'] - 0.8, location_dict['IDF']['longitude'] + 0.8))
    axins.set_ylim(fr_map(location_dict['IDF']['latitude'] - 0.3, location_dict['IDF']['latitude'] + 0.3))

    submapIDF_contract_type = Basemap(projection='tmerc', resolution='l', area_thresh=1000,
                                      llcrnrlon=location_dict['IDF']['longitude'] - 0.8,
                                      llcrnrlat=location_dict['IDF']['latitude'] - 0.3,
                                      urcrnrlon=location_dict['IDF']['longitude'] + 0.8,
                                      urcrnrlat=location_dict['IDF']['latitude'] + 0.3,
                                      epsg=2192, ax=axins)
    submapIDF_contract_type.drawmapboundary()

    for city in location_dict.iterkeys():
        if location_dict[city]['isinIDF']:
            #print city + " " + str(location_dict[city]['count'])
            x, y = submapIDF_contract_type(location_dict[city]['longitude'], location_dict[city]['latitude'])
            ratio_list = get_contract_type_ratios(location_dict[city])
            draw_pie(axins, ratios=ratio_list, X=x, Y=y, size=600)
            # submapIDF_contract_type.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count']/2), alpha=0.5)
            plt.text(x, y, city)

    plt.savefig(os.path.join(output_dir, 'figure_4_2.svg'), bbox_inches='tight')
    plt.close()

    ########################
    fig, ax, fr_map = init_france_map()

    for city in location_dict.iterkeys():
        if not location_dict[city]['isinIDF']:
            #print city + " " + str(location_dict[city]['count'])
            x, y = fr_map(location_dict[city]['longitude'], location_dict[city]['latitude'])
            ratio_list = get_contract_subtype_ratios(location_dict[city])
            draw_pie(ax, ratios=ratio_list, X=x, Y=y, size=600)
            # map_contract_type.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count']/2), alpha=0.5)
            plt.text(x, y, city.decode('utf8'))

    axins = zoomed_inset_axes(ax, 3.5, loc=3)
    # NE 49.241299, 3.55852
    # SW 48.120319, 1.4467
    axins.set_xlim(fr_map(location_dict['IDF']['longitude'] - 0.8, location_dict['IDF']['longitude'] + 0.8))
    axins.set_ylim(fr_map(location_dict['IDF']['latitude'] - 0.3, location_dict['IDF']['latitude'] + 0.3))

    submapIDF_subcontract_type = Basemap(projection='tmerc', resolution='l', area_thresh=1000,
                                         llcrnrlon=location_dict['IDF']['longitude'] - 0.8,
                                         llcrnrlat=location_dict['IDF']['latitude'] - 0.3,
                                         urcrnrlon=location_dict['IDF']['longitude'] + 0.8,
                                         urcrnrlat=location_dict['IDF']['latitude'] + 0.3,
                                         epsg=2192, ax=axins)
    submapIDF_subcontract_type.drawmapboundary()

    for city in location_dict.iterkeys():
        if location_dict[city]['isinIDF']:
            #print city + " " + str(location_dict[city]['count'])
            x, y = submapIDF_subcontract_type(location_dict[city]['longitude'], location_dict[city]['latitude'])
            ratio_list = get_contract_subtype_ratios(location_dict[city])
            draw_pie(axins, ratios=ratio_list, X=x, Y=y, size=600)
            # submapIDF_contract_type.plot(x, y, marker='o', color='m', markersize=int(location_dict[city]['count']/2), alpha=0.5)
            plt.text(x, y, city.decode('utf8'))

    plt.savefig(os.path.join(output_dir, 'figure_4_3.svg'), bbox_inches='tight')
    plt.close()
