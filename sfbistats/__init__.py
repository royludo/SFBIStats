#! -*- coding:utf-8 -*-

"""
This package contains the code to analyze SFBI job pool.
The related article on bioinfo-fr is available at:
    http://bioinfo-fr.net/etat-de-lemploi-bioinformatique-en-france-analyse-des-offres-de-la-sfbi

"""
from . import job_offer
from . import utils
try:
    from . import loader
except ImportError:
    pass # if the all option was not used, the loader is not installed
