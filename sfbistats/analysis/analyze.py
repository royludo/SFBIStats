# -*- coding: utf-8 -*-
""" Analyze

Main script.
Define some global matplotlib style.
Load the data and then run the modules who produce the plots.

"""

import json
import argparse
import matplotlib.pyplot as plt
from bson import json_util
import os
import sfbistats.analysis.utils as sfbi_utils


import sfbistats.job_offer as sfbi_job
import sfbistats.analysis.time_series as sfbi_time_series
import sfbistats.analysis.summary as sfbi_summary
import sfbistats.analysis.lexical_analysis as sfbi_lexical_analysis
import sfbistats.analysis.maps as sfbi_maps

plt.style.use('fivethirtyeight')
plt.rcParams['axes.prop_cycle'] = plt.cycler('color', sfbi_utils.get_colors())
# for the pie charts
plt.rcParams['patch.linewidth'] = 1
plt.rcParams['patch.edgecolor'] = 'white'

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
    for l in file.readlines():
        # use dict instead of directly object, better with pandas
        job = sfbi_job.JobOfferAnon.from_json(json.loads(l, object_hook=json_util.object_hook)).to_dict()
        job['city'] = sfbi_utils.sanitize_city_name(job['city'])
        job['duration'] = sfbi_utils.sanitize_duration(job['duration'])
        job_list.append(job)
    return job_list

if __name__ == '__main__':

    # parse and check arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--json', required=True, type=file)
    argparser.add_argument('--output_dir', required=True)
    args = vars(argparser.parse_args())
    input_file = args['json']
    output_dir = args['output_dir']
    if not os.path.exists(output_dir):
        raise ValueError('output_dir argument ' + str(output_dir)+' does not exist.')
    if not os.path.isdir(output_dir):
        raise ValueError('output_dir argument ' + str(output_dir)+' is not a directory.')
    output_dir = os.path.abspath(output_dir)
    print str(input_file)+' '+output_dir

    # load the data
    job_list = load_from_json(input_file)

    # run the scripts
    sfbi_summary.run(job_list, output_dir)
    #lexical_analysis.run(job_list, output_dir) # can't be run on JobOfferAnon
    sfbi_time_series.run(job_list, output_dir)
    sfbi_maps.run(job_list, output_dir)
