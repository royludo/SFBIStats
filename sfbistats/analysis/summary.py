# -*- coding: utf-8 -*-
""" Summary

Provide some basic, global stats.

"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import sfbistats.analysis.utils as sfbi_utils
import numpy as num


def minimal_hbar(ss, figsize=(6, 3)):
    tot = ss.values.sum()
    ss = ss.sort_values(ascending=True)
    labels = ss.index.get_values()
    labelAsX = num.arange(len(labels)) + 0.5
    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(labelAsX, ss.values, align='center', color='cornflowerblue', height=0.8)
    ax.set_yticks(labelAsX)
    ax.set_yticklabels(labels)
    ax.set_xticks([])
    ax.grid(False)
    ax.set_ylim(0, labelAsX[-1] + 1)
    ax.set_xlim(0, max(ss.values * 1.15))
    for pos, n in zip(labelAsX, ss.values):
        perc = 100 * float(n) / tot
        ax.annotate('{0:.1f}%'.format(perc), xy=(n + (max(ss.values) * 0.01), pos), va='center')
        ax.annotate(str(n), xy=(n - (max(ss.values * 0.01)), pos), va='center', ha='right')
    return fig, ax


def run(job_list, output_dir):
    print "Running summary.py"
    contract_subtype_level = {'Post-doc / IR': 'PhD',
                              'PR': 'PhD',
                              'MdC': 'PhD',
                              'CR': 'PhD',
                              'IR': 'PhD',
                              'ATER': 'PhD',
                              u'CDD Ingénieur': 'Master',
                              'IE': 'Master'}
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
    summary_file.write(pd.Series(df.contract_type).value_counts().to_string(header=False).encode('utf8') + "\n")

    # general types ratios pie chart
    df_contract_type_count = pd.Series(df.contract_type).value_counts(sort=True)
    fig, ax = minimal_hbar(df_contract_type_count)
    ax.set_title(u'Types de postes')
    fig.savefig(os.path.join(output_dir, 'summary_6.svg'), bbox_inches='tight')
    plt.close(fig)

    plt.figure()
    ax = df_contract_type_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de poste', y=1.08)
    plt.savefig(os.path.join(output_dir, 'summary_1.svg'), bbox_inches='tight')
    plt.close()

    # CDI subtypes ratios pie chart
    df_contract_subtype_CDI_count = pd.Series(df[df.contract_type == 'CDI'].contract_subtype).value_counts(sort=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDI_count)
    ax.set_title(u'Types de CDI')
    fig.savefig(os.path.join(output_dir, 'summary_7.svg'), bbox_inches='tight')
    plt.close(fig)

    plt.figure()
    ax = df_contract_subtype_CDI_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDI', y=1.08)
    plt.savefig(os.path.join(output_dir, 'summary_2.svg'), bbox_inches='tight')
    plt.close()

    # CDD subtypes ratios pie chart
    df_contract_subtype_CDD_count = pd.Series(df[df.contract_type == 'CDD'].contract_subtype).value_counts(sort=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDD_count)
    ax.set_title(u'Types de CDD')
    fig.savefig(os.path.join(output_dir, 'summary_8.svg'), bbox_inches='tight')
    plt.close(fig)

    plt.figure()
    ax = df_contract_subtype_CDD_count.plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title('Types de CDD', y=1.08)
    plt.savefig(os.path.join(output_dir, 'summary_3.svg'), bbox_inches='tight')
    plt.close()

    # best cities
    df_city = pd.Series(df.city).value_counts()
    # df_city = df_city[df_city >= 10]
    sum_small_cities = df_city.iloc[16:].sum()
    df_city = df_city.iloc[:15]
    df_city['Autres'] = sum_small_cities
    # plt.figure()
    city_names = df_city.index
    labels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(city_names, 100. * df_city / df_city.sum())]
    # [' '] * len(labels) -> empty labels for each pie, to avoid matplotlib warning
    axes = pd.DataFrame(df_city).plot(kind='pie', startangle=90, labels=[' '] * len(labels), colors=colors,
                                      subplots=True)
    for ax in axes:
        ax.legend(labels, loc=1, bbox_to_anchor=(1.5, 1.1))
        ax.set_xlabel('')
        ax.set_ylabel('')
    plt.axis('equal')
    plt.title("Parts des 15 villes ayant le plus d'offres d'emploi", y=1.08)
    plt.savefig(os.path.join(output_dir, 'summary_4.svg'), bbox_inches='tight')
    plt.close()

    # education level ratios pie chart
    df_study_level = pd.Series(df.contract_subtype).value_counts(sort=True)
    level_dict = {'PhD': 0, 'Master': 0}
    for subtype in df_study_level.index:
        if subtype in contract_subtype_level:
            level = contract_subtype_level[subtype]
            level_dict[level] += df_study_level[subtype]
    plt.figure()
    ax = pd.Series(level_dict).plot(kind='pie', startangle=90, autopct='%1.1f%%', colors=colors)
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.axis('equal')
    plt.title(u'Niveau de diplôme requis pour les CDD et CDI', y=1.08)
    plt.savefig(os.path.join(output_dir, 'summary_5.svg'), bbox_inches='tight')
    plt.close()

    # per city contract types
    city_gb = df.groupby('city')
    df_type_city = city_gb.contract_type.value_counts(sort=True, ascending=True).unstack(level=-1).fillna(0)
    df_type_city['Total'] = df_type_city.sum(axis='columns')
    df_perc_city = df_type_city.div(df_type_city['Total'], axis='index')
    df_perc_city['Total'] = df_type_city['Total']
    df_perc_city = df_perc_city.sort_values(by='Total')
    fig, ax = plt.subplots()
    ax = df_perc_city.loc[:, ['CDD', 'CDI', 'Stage', u'Thèse']].iloc[-10:].plot(ax=ax, kind='barh', stacked=True,
                                                                                color=colors)
    ax.set_xlim([0, 1])
    ax.set_ylabel('')
    i = 0
    for total in df_perc_city['Total'].iloc[-10:]:
        ax.text(1.02, i, int(total), va='center')
        i += 1
    plt.title(u"Répartition des types d'offres\ndans les 10 villes ayant le plus d'offres", y=1.08)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=4)
    fig.savefig(os.path.join(output_dir, 'summary_9.svg'), bbox_inches='tight')
    plt.close(fig)

    # per city education level
    def get_jobs_educ_level(series):
        level_dict = {'PhD': 0, 'Master': 0}
        for e in series.index:
            if e in contract_subtype_level:
                level_dict[contract_subtype_level[e]] += series[e]
        return pd.Series(level_dict)

    def count_master(series):
        return get_jobs_educ_level(series.value_counts())['Master']

    def count_phd(series):
        return get_jobs_educ_level(series.value_counts())['PhD']

    df_level_city = city_gb.contract_subtype.aggregate({'Master': count_master, 'PhD': count_phd})
    df_level_city['Total'] = df_level_city['Master'] + df_level_city['PhD']
    df_level_perc = df_level_city.div(df_level_city['Total'], axis='index')
    df_level_perc['Total'] = df_level_city['Total']
    df_level_perc = df_level_perc.sort_values(by='Total')
    fig, ax = plt.subplots()
    ax = df_level_perc.loc[:, ['Master', 'PhD']].iloc[-10:].plot(ax=ax, kind='barh', stacked=True, color=colors)
    ax.set_xlim([0, 1])
    ax.set_ylabel('')
    i = 0
    for total in df_level_perc['Total'].iloc[-10:]:
        ax.text(1.02, i, int(total), va='center')
        i += 1
    plt.title(u"Proportion des niveaux de diplôme requis\ndans les 10 villes ayant le plus d'offres", y=1.08)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=4)
    fig.savefig(os.path.join(output_dir, 'summary_10.svg'), bbox_inches='tight')
    plt.close(fig)
