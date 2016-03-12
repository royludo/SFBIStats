# -*- coding: utf-8 -*-
""" Summary

Provide some basic, global stats.

"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import sfbistats.analysis.utils as sfbi_utils
import numpy as num
import geopy
import sys

def minimal_hbar(ss, figsize=(6,3)):
    tot = ss.values.sum()
    labels = ss.index.get_values()
    labelAsX = num.arange(len(labels))+0.5
    fig, ax  = plt.subplots(figsize=figsize)
    ax.barh(labelAsX, ss.values, align='center', color='grey')
    ax.set_yticks(labelAsX)
    ax.set_yticklabels(labels)
    ax.set_ylim(0, labelAsX[-1]+1)
    ax.set_xlim(0, max(ss.values*1.15))
    ax.set_xlabel(u"Nombre d'offres")
    ax.grid(axis='x')
    for pos, n in zip(labelAsX, ss.values):
        perc = 100*float(n)/tot
        ax.annotate('{0:.1f}%'.format(perc), xy=(n + (max(ss.values * 0.01)), pos), color='k', fontsize=8, va='center')
    return fig, ax


def run(job_list, output_dir):
    print "Running summary.py"
    contract_type_labels = ['Stage', u'Thèse', 'CDD', 'CDI']
    contract_subtype_labels = {'CDI': ['PR', 'MdC', 'CR', 'IR', 'IE', 'CDI autre'],
                               'CDD': ['Post-doc / IR', u'CDD Ingénieur', 'ATER', 'CDD autre']}
    phd_level = ['Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER']
    master_level = [u'CDD Ingénieur', 'IE']
    colors = sfbi_utils.get_colors()

    df = pd.DataFrame(job_list, columns=['_id', 'contract_type', 'contract_subtype',
                                         'city', 'department', 'region', 'submission_date'])

    summary_file = open(os.path.join(output_dir, 'summary.txt'), 'w')
    submission_date_series = pd.Series(df.submission_date)
    summary_file.write("From " + str(submission_date_series.min()) + " to " + str(submission_date_series.max()) + '\n')
    summary_file.write("Total jobs: " + str(len(df.index)) + "\n")
    summary_file.write(pd.Series(df.contract_type).value_counts().to_string(header=False).encode(
        'utf8') + "\n")  # global contract type proportions

    # Contract type
    df_contract_type_count = pd.Series(df.contract_type).value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_type_count)
    ax.set_title(u'Répartition des types de contrats (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'contract_type.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # CDI subtypes
    df_contract_subtype_CDI_count = pd.Series(df[df.contract_type == 'CDI'].contract_subtype).value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDI_count)
    ax.set_title(u'Répartition des types de CDI (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'cdi_subtype.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # CDD subtypes
    df_contract_subtype_CDD_count = pd.Series(df[df.contract_type == 'CDD'].contract_subtype).value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_contract_subtype_CDD_count)
    ax.set_title(u'Répartition des types de CDD (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'cdd_subtype.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Region repartition
    df_region_count = pd.Series(df.region).value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_region_count, figsize=(6,7))
    ax.set_title(u'Répartition des offres par régions (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'regions.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)

    # Department repartition
    df_dept_count = pd.Series(df.department).value_counts(sort=True, ascending=True)
    fig, ax = minimal_hbar(df_dept_count, figsize=(6,10))
    ax.set_title(u'Répartition des offres par département (2012-2016)')
    fig.savefig(os.path.join(output_dir, 'departements.svg'),
            bbox_inches='tight')
    plt.close(fig); del(fig)
