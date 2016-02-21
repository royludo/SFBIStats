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
    plt.figure(figsize=(10, 0.75*len(labels)))
    plt.barh(labelAsX, ss.values, align='center', color='cornflowerblue', height=0.8)
    plt.yticks(labelAsX, labels)
    plt.xticks([])
    plt.grid(False)
    for pos, n in zip(labelAsX, ss.values):
        plt.annotate(str(n), xy=(n + (max(ss.values * 0.01)) , pos))
    plt.title('Types de poste', y=1.08)
    plt.savefig(output, bbox_inches='tight')


def run(job_list, output_dir):

    contract_type_labels = ['CDI', 'CDD', 'Stage', u'Thèse']
    contract_subtype_labels = { 'CDI': ['PR', 'MdC', 'CR', 'IR', 'IE', 'CDI autre'],
                                'CDD': ['Post-doc / IR', u'CDD Ingénieur', 'ATER', 'CDD autre']}
    phd_level = ['Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER']
    master_level = [u'CDD Ingénieur', 'IE' ]
    colors = sfbi_utils.get_colors()

    df = pd.DataFrame(job_list, columns=['_id', 'contract_type', 'contract_subtype', 'city', 'submission_date'])

    summary_file = open(os.path.join(output_dir, 'summary.txt'), 'w')
    submission_date_series = pd.Series(df.submission_date)
    summary_file.write("From "+ str(submission_date_series.min())+" to "+str(submission_date_series.max())+'\n')
    summary_file.write("Total jobs: "+str(len(df.index))+"\n")
    summary_file.write(pd.Series(df.contract_type).value_counts().to_string(header=False).encode('utf8')+"\n")  # global contract type proportions

    # general types ratios pie chart
    df_contract_type_count = pd.Series(df.contract_type).value_counts(sort=True)
    minimal_hbar(df_contract_type_count, os.path.join(output_dir,'figure_1_6.png'))
    plt.figure()
    ax = df_contract_type_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de poste', y=1.08)
    plt.savefig(os.path.join(output_dir,'figure_1_1.png'), bbox_inches='tight')
    plt.close()


    # CDI subtypes ratios pie chart
    df_contract_subtype_CDI_count = pd.Series(df[df.contract_type == 'CDI'].contract_subtype).value_counts(sort=True)
    minimal_hbar(df_contract_subtype_CDI_count, os.path.join(output_dir,'figure_1_7.png'))
    plt.figure()
    ax = df_contract_subtype_CDI_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDI', y=1.08)
    plt.savefig(os.path.join(output_dir,'figure_1_2.png'), bbox_inches='tight')
    plt.close()

    # CDD subtypes ratios pie chart
    df_contract_subtype_CDD_count = pd.Series(df[df.contract_type == 'CDD'].contract_subtype).value_counts(sort=True)
    minimal_hbar(df_contract_subtype_CDD_count, os.path.join(output_dir,'figure_1_8.png'))
    plt.figure()
    ax = df_contract_subtype_CDD_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDD', y=1.08)
    plt.savefig(os.path.join(output_dir,'figure_1_3.png'), bbox_inches='tight')
    plt.close()

    # best cities
    df_city = pd.Series(df.city).value_counts()
    #df_city = df_city[df_city >= 10]
    sum_small_cities = df_city[df_city < 15].sum()
    df_city = df_city[df_city >= 15]
    df_city['Autres'] = sum_small_cities
    #plt.figure()
    axes = pd.DataFrame(df_city).plot(kind='pie', startangle=90, labels=None, colors=colors, subplots=True)
    city_names = df_city.index
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(city_names, 100.*df_city/df_city.sum())]
    for ax in axes:
        ax.legend(labels, loc=1, bbox_to_anchor=(1.5, 1.1))
        ax.set_xlabel('')
        ax.set_ylabel('')
    plt.axis('equal')
    plt.title("Parts des villes ayant plus de 15 offres d'emploi", y=1.08)
    plt.savefig(os.path.join(output_dir,'figure_1_4.png'), bbox_inches='tight')
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
    plt.savefig(os.path.join(output_dir,'figure_1_5.png'), bbox_inches='tight')
    plt.close()
