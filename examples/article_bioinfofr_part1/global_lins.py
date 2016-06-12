# -*- coding: utf-8 -*-
""" Summary

Provide some basic, global stats.

"""

import matplotlib.pyplot as plt
import pandas as pd
import os
from sfbistats import utils as sfbi_utils
import numpy as num


def minimal_hbar(ss, figsize=(6,3)):
    tot = ss.values.sum()
    labels = ss.index.get_values()
    labelAsX = num.arange(len(labels))+1
    fig, ax  = plt.subplots(figsize=figsize)
    ax.barh(labelAsX, ss.values, align='center', color='grey')
    ax.set_yticks(labelAsX)
    ax.set_yticklabels(labels)
    ax.set_ylim(0, labelAsX[-1]+1)
    ax.set_xlim(0, max(ss.values*1.15))
    ax.set_xlabel(u"Nombre d'offres")
    ax.grid(axis='x')
    plt.setp(ax.get_yticklines(), visible=False)
    for pos, n in zip(labelAsX, ss.values):
        perc = 100*float(n)/tot
        ax.annotate('{0:.1f}%'.format(perc),
                    xy=(n + (max(ss.values * 0.01)), pos),
                    color='k', fontsize=8, va='center')
    return fig, ax

def minimal_violinplot(ss, figsize=(6,3)):
    labels = ss.index.get_values()
    data = [ss[x] for x in labels]
    labelAsX = num.arange(len(labels))+1
    fig, ax = plt.subplots(figsize=figsize)
    violin_parts = ax.violinplot(data,
            vert=False,
            positions=labelAsX,
            showextrema=False,
            showmedians=True)
    for pc in violin_parts['bodies']:
            pc.set_facecolor('gray')
            pc.set_edgecolor('black')
    ax.set_yticks(labelAsX)
    ax.set_yticklabels(labels)
    ax.grid(axis='y')
    maxvalue = max(max(x) for x in data)
    for pos, n in zip(labelAsX, data):
        tot = len(n)
        ax.annotate(tot,
                xy=(0.9*maxvalue, pos+0.1),
                color='k', fontsize=12, va='center', ha='center')
    return fig, ax

def run(job_list, output_dir):
    print ("Running global_lins.py...")
    contract_type_labels = ['Stage', u'Thèse', 'CDD', 'CDI']
    contract_subtype_labels = {'CDI': ['PR', 'MdC', 'CR',
                                        'IR', 'IE', 'CDI autre'],
                               'CDD': ['Post-doc / IR',
                                       u'CDD Ingénieur', 'ATER',
                                       'CDD autre']}
    # Dictionnary to convert subtype to level
    contract_subtype_level = dict.fromkeys(['Post-doc / IR',
                                            'PR',
                                            'MdC',
                                            'CR',
                                            'IR',
                                            'ATER'], 'PhD')
    contract_subtype_level.update(dict.fromkeys([u'CDD Ingénieur', 'IE'], 'Master'))


    # Define colors using a color map
    #colors = plt.get_cmap('nipy_spectral')(num.linspace(0,0.8,4))
    #colors = map(lambda rgb:
    #        '#%02x%02x%02x' % (rgb[0]*255,rgb[1]*255,rgb[2]*255),
    #                           tuple(colors[:,0:-1]))
    # Define colors using bioinfo-fr color palette
    colors = ['#6f3883', '#87ad3e', '#fce33e', '#4066c7', '#cc3428']
    plt.rcParams.update(plt.rcParamsDefault)

    df = pd.DataFrame(job_list, columns=['contract_type',
                                         'contract_subtype',
                                         'city',
                                         'department',
                                         'region',
                                         'duration',
                                         'submission_date'])

    # Contract type
    df_contract_type_count = df.contract_type.\
            value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_type_count)
    ax.set_title(u'Répartition des types de contrats (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_1.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # CDI subtypes
    df_contract_subtype_CDI_count = df[df.contract_type == 'CDI'].\
            contract_subtype.\
            value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDI_count)
    ax.set_title(u'Répartition des types de CDI (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_2.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # CDD subtypes
    df_contract_subtype_CDD_count = df[df.contract_type == 'CDD'].\
            contract_subtype.\
            value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDD_count)
    ax.set_title(u'Répartition des types de CDD (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_3.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Region repartition
    df_region_count = df.region.\
            value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_region_count, figsize=(6,7))
    ax.set_title(u'Répartition des offres par région (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_4.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Department repartition
    df_dept_count = df.department.\
            value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_dept_count, figsize=(6,10))
    ax.set_title(u'Répartition des offres par département (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_5.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Education level
    def get_jobs_educ_level(Series):
        level_dict = {'PhD': 0, 'Master': 0}
        for e in Series.index:
            if e in contract_subtype_level:
                level_dict[contract_subtype_level[e]] +=  Series[e]
        return pd.Series(level_dict)
    df_study_level = df.contract_subtype.\
            value_counts(sort=True)
    level_series = get_jobs_educ_level(df_study_level)
    fig, ax = minimal_hbar(level_series)
    ax.set_title(u'Diplôme minimal requis (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_6.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Education level per region
    # We take advantage of groupby (Pandas) and use
    # the same function as above
    gb_region = df.groupby('region')
    def count_master(Series):
        return get_jobs_educ_level(Series.value_counts())['Master']
    def count_phd(Series):
        return get_jobs_educ_level(Series.value_counts())['PhD']
    df_level_region = gb_region.contract_subtype.\
            aggregate({'Master': count_master, 'PhD': count_phd})
    df_level_region['Total'] = df_level_region.sum(axis='columns')
    df_level_region['Master'] = (df_level_region['Master'] /
                                 df_level_region['Total'])
    df_level_region['PhD'] = (df_level_region['PhD'] /
                              df_level_region['Total'])

    df_level_region = df_level_region.sort_values(by='Total')
    fig, ax = plt.subplots()
    df_level_region.loc[:, ['Master', 'PhD']].\
            plot(ax=ax, kind='barh', stacked=True, color=colors)
    ax.set_xlim([0,1])
    ax.set_ylabel('')
    plt.setp(ax.get_yticklines(), visible=False)
    i = 0
    for total in df_level_region['Total']:
        ax.text(1.02, i-0.15, total)
        i += 1
    ax.set_title(u"Proportion des diplômes requis par région (2012-2016)")
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, bbox_to_anchor=(0.75, -0.05), ncol=2)
    fig.savefig(os.path.join(output_dir, 'summary_lins_7.svg'),
                bbox_inches='tight')
    plt.close(fig); del(fig)

    # Contract type per region
    # Here again we take advantage of groupby
    gb_region = df.groupby('region')
    df_type_region = gb_region.contract_type.\
            value_counts(sort=True, ascending=True).\
            unstack(level=-1).\
            fillna(0)# value_counts return NaN if not present
    df_type_region['Total'] = df_type_region.sum(axis='columns')
    df_perc_region = df_type_region.\
            div(df_type_region['Total'], axis='index')
    df_perc_region['Total'] = df_type_region['Total'].astype(int)

    df_perc_region = df_perc_region.sort_values(by='Total')
    fig, ax = plt.subplots()
    df_perc_region.loc[:, [u'Thèse', 'Stage', 'CDI', 'CDD']].\
            plot(ax=ax, kind='barh', stacked=True, color=colors)
    ax.set_xlim([0,1])
    ax.set_ylabel('')
    plt.setp(ax.get_yticklines(), visible=False)
    i = 0
    for total in df_perc_region['Total']:
        ax.text(1.02, i-0.15, total)
        i += 1
    ax.set_title(u"Proportion des postes par région (2012-2016)")
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, bbox_to_anchor=(0.98, -0.05), ncol=4)
    fig.savefig(os.path.join(output_dir, 'summary_lins_8.svg'),
        bbox_inches='tight')
    plt.close(fig); del(fig)

    # Duration of CDD
    dict_categories = {u'≤ 6 mois': lambda x: 0<x<=6,
                       u'6 < x ≤ 12 mois': lambda x: 6<x<=12,
                       u'12 < x ≤ 18 mois': lambda x: 12<x<=18,
                       u'18 < x ≤ 24 mois': lambda x: 18<x<=24,
                       u'24 < x ≤ 30 mois': lambda x: 24<x<=30,
                       u'30 < x ≤ 36 mois': lambda x: 30<x<=36,
                       u'> 36 mois': lambda x: x>36}
    list_categories = [u'≤ 6 mois',
                       u'6 < x ≤ 12 mois',
                       u'12 < x ≤ 18 mois',
                       u'18 < x ≤ 24 mois',
                       u'24 < x ≤ 30 mois',
                       u'30 < x ≤ 36 mois',
                       u'> 36 mois']
    def get_category(months):
        for key, func in dict_categories.items():
            if func(months): return key

    is_CDD = df.contract_type == 'CDD'
    is_sanitized = (0 < df.duration) & (df.duration < 100)
    df_duration = df[is_CDD & is_sanitized][['contract_subtype','duration', 'region']]
    df_duration['category'] = df_duration.loc[:,'duration'].apply(get_category)

    ## Global duration of CDD
    df_categories = df_duration.category.value_counts().reindex(list_categories)
    fig, ax = minimal_hbar(df_categories)
    ax.set_title(u'Répartition des durées de CDD (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'summary_lins_9.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    ## Duration of CDD per contract subtype
    gb_duration_by_contract = df_duration.groupby('contract_subtype')['duration']
    df_duration_by_contract = gb_duration_by_contract.\
            apply(lambda x: x.tolist()).to_frame()
    df_duration_by_contract['Total'] = df_duration_by_contract['duration'].str.len()
    df_duration_by_contract = df_duration_by_contract.sort_values(by='Total').duration
    fig, ax = minimal_violinplot(df_duration_by_contract, figsize=(8,6))

    ax.set_title(u'Répartition des durées de CDD par type de contrat (2012-2016)')
    ax.set_xlabel(u'Durée (mois)')
    xticks = range(0,66,6)
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(x) for x in xticks])
    fig.savefig(os.path.join(output_dir, 'summary_lins_10.svg'),
        bbox_inches='tight')
    plt.close(fig); del(fig)

    ## Duration of CDD per region
    gb_duration_by_region = df_duration.groupby('region')['duration']
    df_duration_by_region = gb_duration_by_region.\
            apply(lambda x: x.tolist()).to_frame()
    df_duration_by_region['Total'] = df_duration_by_region['duration'].str.len()
    df_duration_by_region = df_duration_by_region.sort_values(by='Total').duration
    fig, ax = minimal_violinplot(df_duration_by_region, figsize=(8,8))

    ax.set_title(u'Répartition des durées de CDD par région (2012-2016)')
    ax.set_xlabel(u'Durée (mois)')
    xticks = range(0,66,6)
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(x) for x in xticks])
    fig.savefig(os.path.join(output_dir, 'summary_lins_11.svg'),
        bbox_inches='tight')
    plt.close(fig); del(fig)
