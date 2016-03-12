# -*- coding: utf-8 -*-
""" Summary

Provide some basic, global stats.

"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import sfbistats.analysis.utils as sfbi_utils


def minimal_hbar(series, output):
    ss = series.sort_values()  # needed for barh
    labels = ss.index.get_values()
    labelAsX = range(len(labels))
    plt.figure(figsize=(10, 0.75 * len(labels)))
    plt.barh(labelAsX, ss.values, align='center', color='cornflowerblue', height=0.8)
    plt.yticks(labelAsX, labels)
    plt.xticks([])
    plt.grid(False)
    for pos, n in zip(labelAsX, ss.values):
        plt.annotate(str(n), xy=(n + (max(ss.values * 0.01)), pos))
    plt.title('Types de poste', y=1.08)
    plt.savefig(output, bbox_inches='tight')
    plt.close()


def run(job_list, output_dir):
    print "Running summary.py"
    contract_type_labels = ['CDI', 'CDD', 'Stage', u'Thèse']
    contract_subtype_labels = {'CDI': ['PR', 'MdC', 'CR', 'IR', 'IE', 'CDI autre'],
                               'CDD': ['Post-doc / IR', u'CDD Ingénieur', 'ATER', 'CDD autre']}
    phd_level = ['Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER']
    master_level = [u'CDD Ingénieur', 'IE']
    colors = sfbi_utils.get_colors()

    plt.style.use('fivethirtyeight')
    plt.rcParams['axes.prop_cycle'] = plt.cycler('color', sfbi_utils.get_colors())
    # for the pie charts
    plt.rcParams['patch.linewidth'] = 1
    plt.rcParams['patch.edgecolor'] = 'white'

    df = pd.DataFrame(job_list, columns=['_id', 'contract_type', 'contract_subtype', 'city', 'submission_date'])

    summary_file = open(os.path.join(output_dir, 'summary.txt'), 'w')
    submission_date_series = pd.Series(df.submission_date)
    summary_file.write("From " + str(submission_date_series.min()) + " to " + str(submission_date_series.max()) + '\n')
    summary_file.write("Total jobs: " + str(len(df.index)) + "\n")
    summary_file.write(pd.Series(df.contract_type).value_counts().to_string(header=False).encode(
        'utf8') + "\n")  # global contract type proportions

    # general types ratios pie chart
    df_contract_type_count = pd.Series(df.contract_type).value_counts(sort=True)
    minimal_hbar(df_contract_type_count, os.path.join(output_dir, 'figure_1_6.svg'))
    plt.figure()
    ax = df_contract_type_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de poste', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_1.svg'), bbox_inches='tight')
    plt.close()

    # CDI subtypes ratios pie chart
    df_contract_subtype_CDI_count = pd.Series(df[df.contract_type == 'CDI'].contract_subtype).value_counts(sort=True)
    minimal_hbar(df_contract_subtype_CDI_count, os.path.join(output_dir, 'figure_1_7.svg'))
    plt.figure()
    ax = df_contract_subtype_CDI_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDI', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_2.svg'), bbox_inches='tight')
    plt.close()

    # CDD subtypes ratios pie chart
    df_contract_subtype_CDD_count = pd.Series(df[df.contract_type == 'CDD'].contract_subtype).value_counts(sort=True)
    minimal_hbar(df_contract_subtype_CDD_count, os.path.join(output_dir, 'figure_1_8.svg'))
    plt.figure()
    ax = df_contract_subtype_CDD_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDD', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_3.svg'), bbox_inches='tight')
    plt.close()

    # best cities
    df_city = pd.Series(df.city).value_counts()
    # df_city = df_city[df_city >= 10]
    sum_small_cities = df_city[df_city < 15].sum()
    df_city = df_city[df_city >= 15]
    df_city['Autres'] = sum_small_cities
    # plt.figure()
    city_names = df_city.index
    labels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(city_names, 100. * df_city / df_city.sum())]
    # [' '] * len(labels) -> empty labels for each pie, to avoid matplotlib warning
    axes = pd.DataFrame(df_city).plot(kind='pie', startangle=90, labels=[' '] * len(labels), colors=colors, subplots=True)
    for ax in axes:
        ax.legend(labels, loc=1, bbox_to_anchor=(1.5, 1.1))
        ax.set_xlabel('')
        ax.set_ylabel('')
    plt.axis('equal')
    plt.title("Parts des villes ayant plus de 15 offres d'emploi", y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_4.svg'), bbox_inches='tight')
    plt.close()

    # education level ratios pie chart
    df_study_level = pd.Series(df.contract_subtype).value_counts(sort=True)
    level_dict = {'PhD': 0, 'Master': 0}
    for e in df_study_level.index:
        if e in phd_level:
            level_dict['PhD'] += df_study_level[e]
        elif e in master_level:
            level_dict['Master'] += df_study_level[e]
    plt.figure()
    ax = pd.Series(level_dict).plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title(u'Niveau de diplôme requis pour les CDD et CDI', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_5.svg'), bbox_inches='tight')
    plt.close()

    df_city2 = pd.Series(df.city).value_counts()
    citytype_dict = dict()
    citysubtype_dict = dict()
    for i in range(0, len(df)):
        city = df.city[i]
        type = df.contract_type[i].encode('utf8')
        subtype = df.contract_subtype[i].encode('utf8')
        if citytype_dict.has_key(city):
            if citytype_dict[city].has_key(type):
                citytype_dict[city][type] += 1
            else:
                citytype_dict[city][type] = 1

            if citysubtype_dict[city].has_key(subtype):
                citysubtype_dict[city][subtype] += 1
            else:
                citysubtype_dict[city][subtype] = 1
        else:
            citytype_dict[city] = dict()
            citytype_dict[city][type] = 1
            citysubtype_dict[city] = dict()
            citysubtype_dict[city][subtype] = 1
    proportion_dict = {'CDD': {}, 'CDI': {}, u'Thèse': {}, 'Stage': {}, 'Total': {}}
    count_dict = {'CDD': {}, 'CDI': {}, u'Thèse': {}, 'Stage': {}}
    subtype_count_dict = {'PR': {}, 'MdC': {}, 'CR': {}, 'IR': {}, 'IE': {}, 'CDI autre': {},
                          'Post-doc / IR': {}, u'CDD Ingénieur': {}, 'ATER': {}, 'CDD autre': {} }
    study_level_dict = {'Master': {}, 'PhD': {}, 'Total': {}}
    for i in range(0,10):
        city = df_city2.index[i]
        total = df_city2[i]
        print str(city)+' '+str(total)
        #proportion_dict[city] = {'CDD': 0, 'CDI': 0, u'Thèse': 0, 'Stage': 0}
        for k,v in citytype_dict[city].iteritems():
            proportion_dict[k.decode('utf8')][city] = citytype_dict[city][k] / float(total)
            count_dict[k.decode('utf8')][city] = citytype_dict[city][k]
        proportion_dict['Total'][city] = total
        for k,v in citysubtype_dict[city].iteritems():
            if k:
                subtype_count_dict[k.decode('utf8')][city] = citysubtype_dict[city][k]

        study_level_dict['PhD'][city] = 0
        study_level_dict['Master'][city] = 0
        subtotal = 0
        for k in phd_level:
            if citysubtype_dict[city].has_key(k.encode('utf8')):
                study_level_dict['PhD'][city] += citysubtype_dict[city][k.encode('utf8')]
                subtotal += citysubtype_dict[city][k.encode('utf8')]
        for k in master_level:
            if citysubtype_dict[city].has_key(k.encode('utf8')):
                study_level_dict['Master'][city] += citysubtype_dict[city][k.encode('utf8')]
                subtotal += citysubtype_dict[city][k.encode('utf8')]
        study_level_dict['Master'][city] /= float(subtotal)
        study_level_dict['PhD'][city] /= float(subtotal)
        study_level_dict['Total'][city] = subtotal

    df_study_level_city = pd.DataFrame(study_level_dict).fillna(0).sort_values(by='Total')
    ax = df_study_level_city.loc[:, ['Master', 'PhD']].plot(kind='barh', stacked=True, color=colors)
    ax.set_xlim([0,1])
    i = 0
    for total in df_study_level_city['Total']:
        ax.text(1.02, i-0.15, total)
        i += 1
    plt.title('Types de poste', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_9.svg'), bbox_inches='tight')

    df_proportion_city = pd.DataFrame(proportion_dict).fillna(0).sort_values(by='Total')
    ax = df_proportion_city.loc[:, ['CDD', 'CDI', 'Stage', u'Thèse']].plot(kind='barh', stacked=True, color=colors)
    ax.set_xlim([0,1])
    i = 0
    for total in df_proportion_city['Total']:
        ax.text(1.02, i-0.15, total)
        i += 1
    plt.title('Types de poste', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_1_10.svg'), bbox_inches='tight')


