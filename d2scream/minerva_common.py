# minerva_common.py: Common functions and definitions for working with Minerva
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import str
from builtins import input
from builtins import range
from builtins import object

import requests,sys
import re
import datetime
from datetime import datetime as dt
from bs4 import BeautifulSoup
from . import shib_credentials

cookie_data = {}
referer = ""
s = requests.Session()
verbose = True

try:
    import html5lib
    parser = 'html5lib'
except ImportError:
    parser = 'html.parser'
    print("""
Warning: Falling back to html.parser; some commands may fail. Installing html5lib is recommended:
    $ pip install html5lib
""")    

def minerva_get(func, base_url = shib_credentials.lms_url):
    """A GET request to minerva that accepts a string: the GET request arguments.
    
    """
    if verbose:
        sys.stderr.write("? " + func + "\n")

    global referer
    url = base_url + func
    r = s.get(url,cookies = cookie_data, headers={'Referer': referer})
    referer = r.url
    return r


def minerva_post(func,req, base_url = shib_credentials.lms_url):
    """A POST request to minerva that accepts a string for URL arguments and the data for the POST request.
    
    """
    if verbose:
        sys.stderr.write("> " + func + "\n")

    global referer
    url = base_url + func
    r = s.post(url,data = req,cookies = cookie_data,headers = {'Referer': referer, 'Content-Type': 'application/x-www-form-urlencoded'})
    referer = r.url
    return r

def get_bldg_abbrev(location):
    """Doesn't really do much. Just tries a few tricks to shorten the names of buildings."""
    subs = {
            'Building': '', 'Hall': '', 'Pavilion': '','House': '','Centre': '', 'Complex': '',
            'Library': 'Lib.', 'Laboratory': 'Lab.',
            'Biology': 'Bio.', 'Chemistry': 'Chem.',' Physics': 'Phys.', 'Engineering': 'Eng.', 'Anatomy': 'Anat.', 'Dentistry': 'Dent.', 'Medical': 'Med.', 'Life Sciences': 'Life Sc.'
    }

    for sub in subs:
        location = location.replace(sub,subs[sub])

    return location

def minervac_sanitize(text):
    """Encodes given text to ASCII"""
    return text.encode('ascii','ignore')

def set_loglevel(set_verbose):
    global verbose
    verbose = set_verbose

def is_verbose():
    global verbose
    return verbose

def normalize(input):
    """ Normalizes text to pure english
    From <http://stackoverflow.com/questions/517923>
    """
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', input)
            if unicodedata.category(c) != 'Mn')

def minerva_parser(text):
    return BeautifulSoup(text,parser)
    


iso_date  = {
        'date': '%Y-%m-%d',
        'time': '%H:%M',
        'full': '%Y%m%dT%H%M%S'
}
