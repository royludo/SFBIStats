# -*- coding: utf-8 -*-
""" Analyze

Main script.
Define some global matplotlib style.
Load the data and then run the modules who produce the plots.

"""
from __future__ import unicode_literals

import json
import argparse
from bson import json_util
import os
import sfbistats.analysis.utils as sfbi_utils
import pkg_resources
import collections


import sfbistats.job_offer as sfbi_job
import sfbistats.analysis.time_series as sfbi_time_series
import sfbistats.analysis.summary as sfbi_summary
import sfbistats.analysis.global_lins as sfbi_global_lins
import sfbistats.analysis.lexical_analysis as sfbi_lexical_analysis
import sfbistats.analysis.maps as sfbi_maps


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
    city_dict = collections.defaultdict(int)
    for l in file.readlines():
        # use dict instead of directly object, better with pandas
        job = sfbi_job.JobOfferAnon.from_json(json.loads(l, object_hook=json_util.object_hook)).to_dict()
        job['city'] = sfbi_utils.sanitize_city_name(job['city'])
        job['city'] = sfbi_utils.sanitize_city_name_for_geoloc(job['city'])
        city_file = pkg_resources.resource_filename('sfbistats.analysis', 'city_locations.csv')
        dep, reg = sfbi_utils.city_to_dep_region(job['city'], city_file)
        job['department'] = dep
        job['region'] = reg
        job['duration'] = sfbi_utils.sanitize_duration(job['duration'])
        city_dict[job['city']] += 1
        job_list.append(job)
    job_list = sfbi_utils.spell_correct(job_list, city_dict)
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
    sfbi_global_lins.run(job_list, output_dir)
    sfbi_lexical_analysis.run(job_list, output_dir)
    sfbi_time_series.run(job_list, output_dir)
    sfbi_maps.run(job_list, output_dir)

    print ("Complete")
