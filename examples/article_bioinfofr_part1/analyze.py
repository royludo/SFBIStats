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


from sfbistats import utils
from sfbistats import job_offer
import summary
import global_lins
import lexical_analysis
import maps

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
    job_list = utils.load_from_json(input_file)

    # run the scripts
    global_lins.run(job_list, output_dir)
    print ("Complete")
