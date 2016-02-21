# -*- coding: utf-8 -*-
""" Time series

Provide some plots on the evolution of quantity and proportion of different contract types.

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mDates
import os


def proportion_stackplot(df, output=None, xlabel='', ylabel='', title=''):
    """
    Pandas has a bug with it's plot(kind='area'). When moving the legend, the colors disappear.
    By default with pandas the legend sits on the graph, which is not a desired behavior.
    So this function imitates panda's formatting of an area plot, with a working well-placed legend.

    Parameters
    ----------
    df : pandas.Dataframe
        x must be a date series.
        y is any number of columns containing percentages that must add up to 100 for each row.
    output : string
        the complete output file name
    xlabel : string
    ylabel : string
    title : string

    Returns
    -------

    """

    column_names = df.columns.values
    x = df.index.date
    column_series_list = []
    for cname in column_names:
        column_series_list.append(pd.Series(df[cname]).tolist())
    fig, ax = plt.subplots()
    polys = ax.stackplot(x, column_series_list, alpha=0.8)
    ax.set_ylim([0, 100])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    legends = []
    for poly in polys:
        legends.append(plt.Rectangle((0, 0), 1, 1, facecolor=poly.get_facecolor()[0]))
    # don't try to understand the legend displacement thing here. Believe me. Don't.
    plt.figlegend(legends, column_names, loc=7, bbox_to_anchor=(1.2+legend_displace_factor(column_names), 0.5))
    plt.title(title, y=1.08)
    date_fmt_year = mDates.DateFormatter('%b\n%Y')
    date_fmt_month = mDates.DateFormatter('%b')
    ax.xaxis.set_major_locator(mDates.YearLocator())
    ax.xaxis.set_major_formatter(date_fmt_year)
    ax.xaxis.set_minor_locator(mDates.MonthLocator(bymonth=7))
    ax.xaxis.set_minor_formatter(date_fmt_month)
    plt.savefig(output, bbox_inches='tight')
    plt.close()

def legend_displace_factor(column_names):
    """
    On a plot, the longer the text of the legend, the further away it needs to be from the plot.
    Else, it overlaps the plot. This needs to be determined manually.

    Get the maximum length of a legend's entry, and then compute the value used to push the legend out of the plot.
    The function used here is completely arbitrary, and has been determined empirically.

    Parameters
    ----------
    column_names :list [string]

    Returns
    -------
    float

    """
    len_list = []
    for n in column_names:
        len_list.append(len(n))
    max_length = max(len_list)
    max_length -= 5
    # ensure it will be positive
    if max_length < 0:
        max_length = 0
    return max_length * 0.015

def run(job_list, output_dir):

    print "Running time_series.py"
    plt.rcParams['lines.linewidth'] = 0
    plt.rcParams['patch.linewidth'] = 0
    # disable silly warning
    pd.options.mode.chained_assignment = None

    df = pd.DataFrame(job_list, columns=['_id','city', 'user', 'submission_date', 'contract_type', 'contract_subtype'])

    df2 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_type}).reset_index().groupby(['type','date'])['index'].count().reset_index(name='count')
    df2_t = df2.pivot(index='date', columns='type', values='count')
    df2_t2 = df2_t.resample('1M', how='sum')
    df2_t2.columns.name = 'Type'
    ax = df2_t2.plot(kind='area')
    plt.title(u'Évolution des types de poste', y=1.08)
    ax.set_xlabel('Date')
    ax.set_ylabel("Nombre d'offres")
    plt.savefig(os.path.join(output_dir, 'figure_3_1.png'), bbox_inches='tight')
    plt.close()

    # just CDD
    df3 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_subtype}).reset_index().groupby(['type','date'])['index'].count().reset_index(name='count')
    tmp = df3['type'].isin(['Post-doc / IR',u'CDD Ingénieur', 'CDD autre', 'ATER'])
    df3 = df3[tmp]
    df3_t = df3.pivot(index='date', columns='type', values='count')
    df3_t2 = df3_t.resample('1M', how='sum')
    df3_t2.columns.name = 'Type'
    ax = df3_t2.plot(kind='area')
    plt.title(u'Évolution des types de CDD', y=1.08)
    ax.set_xlabel('Date')
    ax.set_ylabel("Nombre d'offres")
    plt.savefig(os.path.join(output_dir, 'figure_3_2.png'), bbox_inches='tight')
    plt.close()

    # just CDI
    df3 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_subtype}).reset_index().groupby(['type','date'])['index'].count().reset_index(name='count')
    tmp = df3['type'].isin(['CDI autre','IE', 'IR', 'PR', 'MdC', 'CR'])
    df3 = df3[tmp]
    df3_t = df3.pivot(index='date', columns='type', values='count')
    df3_t2 = df3_t.resample('1M', how='sum')
    df3_t2.columns.name = 'Type'
    ax = df3_t2.plot(kind='area')
    plt.title(u'Évolution des types de CDI', y=1.08)
    ax.set_xlabel('Date')
    ax.set_ylabel("Nombre d'offres")
    plt.savefig(os.path.join(output_dir, 'figure_3_3.png'), bbox_inches='tight')
    plt.close()

    df4 = pd.DataFrame({'date': pd.to_datetime(df.submission_date)}).reset_index().groupby('date')['index'].count()
    df4_t = df4.resample('1M', how='sum')
    plt.figure()
    ax = df4_t.plot(linewidth=4)
    plt.title(u"Évolution du nombre total d'offre", y=1.08)
    ax.set_xlabel('Date')
    ax.set_ylabel("Nombre d'offres")
    plt.savefig(os.path.join(output_dir, 'figure_3_4.png'), bbox_inches='tight')
    plt.close()

    '''
        contract type proportions
    '''
    # get the interesting fields and count the type for each date
    df5= pd.DataFrame({'date': df.submission_date, 'type': df.contract_type}).reset_index().groupby(['date','type'])['index'].count().reset_index(name='count')
    # have all the types as column and each date as one line
    df5_t = df5.pivot(index='date', columns='type', values='count')
    # make it per month
    df5_t2 = df5_t.resample('1M', how='sum').fillna(0)
    # add a total column to compute ratio
    df5_t2['total'] = df5_t2.CDD + df5_t2.CDI + df5_t2.Stage+ df5_t2[u'Thèse']
    # replace all the values by ratios
    df5_t3 = pd.DataFrame(df5_t2).apply(lambda x: (x / x['total'] * 100), axis=1).fillna(0).drop('total', 1)
    df5_t3.columns.name = 'Type'
    proportion_stackplot(df5_t3, output=os.path.join(output_dir, 'figure_3_5.png'), xlabel='Date', ylabel='%des offres',
                         title=u"Évolution de la proportion des types de poste")

    '''
        contract subtype proportions for CDI
    '''
    # get the interesting fields only for CDI
    df6 = pd.DataFrame({'date': df.submission_date, 'subtype': df.contract_subtype})[df['contract_type'] == 'CDI'].reset_index()
    # count subtype for each date
    df6 = df6.groupby(['date','subtype'])['index'].count().reset_index(name='count')
    # have all the types as column and each date as one line
    df6_t = df6.pivot(index='date', columns='subtype', values='count')
    # make it per month
    df6_t2 = df6_t.resample('1M', how='sum').fillna(0)
    # add a total column to compute ratio
    df6_t2['total'] = df6_t2['CDI autre'] + df6_t2.CR + df6_t2.IE + df6_t2.IR + df6_t2.MdC + df6_t2.PR
    # replace all the values by ratios
    df6_t3 = pd.DataFrame(df6_t2).apply(lambda x: (x / x['total'] * 100), axis=1).fillna(0).drop('total', 1)
    df6_t3.columns.name = 'Type'
    proportion_stackplot(df6_t3, output=os.path.join(output_dir, 'figure_3_6.png'), xlabel='Date', ylabel='%des offres',
                         title=u"Évolution de la proportion des types de CDI")

    '''
        contract subtype proportions for CDD
    '''
    # get the interesting fields only for CDD
    df7 = pd.DataFrame({ '_id': df._id, 'date': df.submission_date, 'subtype': df.contract_subtype})[df['contract_type'] == 'CDD'].reset_index()
    # count subtype for each date
    df7 = df7.groupby(['date','subtype'])['index'].count().reset_index(name='count')
    # have all the types as column and each date as one line
    df7_t = df7.pivot(index='date', columns='subtype', values='count')
    # make it per month
    df7_t2 = df7_t.resample('1M', how='sum').fillna(0)
    # add a total column to compute ratio
    df7_t2['total'] = df7_t2.ATER + df7_t2[u'CDD Ingénieur'] + df7_t2['CDD autre'] + df7_t2['Post-doc / IR']
    # replace all the values by ratios
    df7_t3 = pd.DataFrame(df7_t2).apply(lambda x: (x / x['total'] * 100), axis=1).fillna(0).drop('total', 1)
    df7_t3.columns.name = 'Type'
    proportion_stackplot(df7_t3, output=os.path.join(output_dir, 'figure_3_7.png'), xlabel='Date', ylabel='%des offres',
                         title=u'Évolution de la proportion des types de CDD')

    # education level quantity
    df8 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_subtype}).reset_index()
    df_bool_master = df8['type'].isin([u'CDD Ingénieur', 'IE' ])
    df_bool_phd = df8['type'].isin(['Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER'])
    df_master = df8[df_bool_master]
    df_master['type'] = 'Master'
    df_phd = df8[df_bool_phd]
    df_phd['type'] = 'PhD'
    df8 = pd.concat([df_phd, df_master]).groupby(['type','date'])['index'].count().reset_index(name='count')
    df8_t = df8.pivot(index='date', columns='type', values='count')
    df8_t2 = df8_t.resample('1M', how='sum').fillna(0)
    df8_t2.columns.name = 'Niveau'
    ax = df8_t2.plot(kind='area')
    ax.set_xlabel('Date')
    ax.set_ylabel("Nombre d'offres")
    plt.title(u"Nombre de CDD et CDI en fonction du niveau de diplôme", y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_3_8.png'), bbox_inches='tight')
    plt.close()

    '''
        education level proportions
    '''
    # add a total column to compute ratio
    df9 = df8_t2
    df9['total'] = df9.Master + df9.PhD
    # replace all the values by ratios
    df9 = pd.DataFrame(df9).apply(lambda x: (x / x['total'] * 100), axis=1).fillna(0).drop('total', 1)
    proportion_stackplot(df9, output=os.path.join(output_dir, 'figure_3_9.png'), xlabel='Date', ylabel='%des offres',
                         title=u'Proportion des niveaux de diplôme requis pour les CDD et CDI')

    '''
       average year series
    '''
    df10 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_type})#.reset_index().groupby(['date'])['index'].count().reset_index(name='count')
    df10 = df10.set_index(pd.DatetimeIndex(df10['date']))
    df10['month'] = df10.index.month
    df10 = (df10['2013':'2015'].groupby(['month', 'type'])['month'].count()/3).reset_index(name='count')
    df10_t = df10.pivot(index='month', columns='type', values='count').fillna(0)
    df10_t.columns.name = 'Type'
    ax = df10_t.plot(linewidth=4)
    ax.set_xlabel('Mois')
    ax.set_ylabel("Nombre d'offres")
    plt.title(u'Moyennes mensuelles 2013-2015', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_3_9.png'), bbox_inches='tight')
    plt.close()

    df11 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_subtype})
    tmp = df11['type'].isin(['Post-doc / IR',u'CDD Ingénieur', 'CDD autre', 'ATER'])
    df11 = df11[tmp]
    df11 = df11.set_index(pd.DatetimeIndex(df11['date']))
    df11['month'] = df11.index.month
    df11 = (df11['2013':'2015'].groupby(['month', 'type'])['month'].count()/3).reset_index(name='count')
    df11_t = df11.pivot(index='month', columns='type', values='count').fillna(0)
    df11_t.columns.name = 'Type'
    ax = df11_t.plot(linewidth=4)
    ax.set_xlabel('Mois')
    ax.set_ylabel("Nombre d'offres")
    plt.title(u'Moyennes mensuelles 2013-2015 pour les CDD', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_3_10.png'), bbox_inches='tight')
    plt.close()

    df12 = pd.DataFrame({'date': df.submission_date, 'type': df.contract_subtype})
    tmp = df12['type'].isin(['CDI autre','IE', 'IR', 'PR', 'MdC', 'CR'])
    df12 = df12[tmp]
    df12 = df12.set_index(pd.DatetimeIndex(df12['date']))
    df12['month'] = df12.index.month
    df12 = (df12['2013':'2015'].groupby(['month', 'type'])['month'].count()/3).reset_index(name='count')
    df12_t = df12.pivot(index='month', columns='type', values='count').fillna(0)
    df12_t.columns.name = 'Type'
    ax = df12_t.plot(linewidth=4)
    plt.legend(loc=7)
    ax.set_xlabel('Mois')
    ax.set_ylabel("Nombre d'offres")
    plt.title(u'Moyennes mensuelles 2013-2015 pour les CDI', y=1.08)
    plt.savefig(os.path.join(output_dir, 'figure_3_11.png'), bbox_inches='tight')
    plt.close()