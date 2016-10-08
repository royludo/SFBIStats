# -*- coding: utf-8 -*-
""" Analyze

Main script.
Define some global matplotlib style.
Load the data and then run the modules who produce the plots.

"""
from __future__ import unicode_literals

import argparse
import os

from sfbistats import utils
import summary
import lexical_analysis
import time_series

if __name__ == '__main__':
    # parse and check arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--json', required=True, type=argparse.FileType('r'))
    argparser.add_argument('--output_dir', required=True)
    args = vars(argparser.parse_args())
    input_file = args['json']
    output_dir = args['output_dir']
    if not os.path.exists(output_dir):
        raise ValueError('output_dir argument ' + str(output_dir)+' does not exist.')
    if not os.path.isdir(output_dir):
        raise ValueError('output_dir argument ' + str(output_dir)+' is not a directory.')
    output_dir = os.path.abspath(output_dir)

    print("Loading and sanitizing data...")
    # load the data
    job_list = utils.load_from_json(input_file)

    # run the scripts
    summary.run(job_list, output_dir)
    lexical_analysis.run(job_list, output_dir)
    time_series.run(job_list, output_dir)
    print("Complete")
