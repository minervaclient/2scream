from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import shib_credentials

import re

def strip_all(elms):
    return [elm.getText().strip() if elm.getText().strip() != "" else None for elm in elms]

def unshift_indent(texts):
    while texts[0] is None:
        texts.pop(0)
    return texts

def dump_grades(f):
    html = minerva_parser(f)
    rows = html.find('table', {'summary': 'List of grade items and their values'}).findAll('tr')
    for row in rows[1:]:
        struct = {}
        if row.has_attr('class') and 'd_ggl1' in row['class']:
            struct['group'] = True
        else: 
            struct['group'] = False

        cols = row.findAll(['td','th'])


        cols = strip_all(cols)   
        cols = unshift_indent(cols)

        if cols[0]:
            struct['title'] = cols[0]

        if cols[1]: 
            struct['points'] = [float(n) for n in cols[1].split(' / ')]

        if cols[2]:
            struct['weight'] = [float(n) for n in cols[2].split(' / ')]
        
        if cols[3]:
            struct['grade'] = float(cols[3].strip(' %'))

        if cols[4]:
            struct['feedback'] = cols[4]
   
        print struct

