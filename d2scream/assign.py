from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import formatters

import re
import json
import dateutil.parser
import datetime


"""
Still to do:
1. Viewing feedback
2. Downloading feedback files
3. Downloading assignment attachments
4. Redownloading your own submissions
5. Making submissions
"""

class Assign(formatters.Formattable):
    def __init__(self):
        self.name = ""
        self.category = False # Is this an assignment or a group of assignments
        self.submitted = None # Has the student submitted this assignment yet?
        self.submit_link = ""
        self.evaluated = None # Has this assignment been evaluated yet?
        self.evaluation_link = ""
        self.evaluation_read = None # Has the evaluation been read?
        self.due_date = None # When is the assignment due?
        self.closed_date = None # When were submissions closed
        self.group = None # The Group of the assignment, if a group assignment


def maybe_date(text):
    try:
        return dateutil.parser.parse(text,fuzzy=True)
    except ValueError:
        # Actually not a date
        return None

def parse_single(cols):
    self = Assign()
    
    self.name = cols[0].find("div",{'class': 'd2l-foldername'}).get_text()

    #### Getting the closure date of the assignment, if applicable
    infos = cols[0].find_all('label')
    for info in infos:
        info = info.get_text()
        if info.startswith('Closed '):
            closure = info.replace('Closed ','')
            self.closed_date = maybe_date(closure)

    #### Getting the group of the assignment, if applicable
    icons = cols[0].find_all('d2l-icon')
    for icon in icons:
        if icon['alt'].startswith('Group: '):
            self.group = icon['alt'].replace('Group: ','')

    #### Getting submission state
    submitted = cols[1].find('a')
    self.submitted = submitted.get_text() == 'Submitted'
    self.submit_link = submitted['href']

    #### Getting evaluation state
    evaluation = cols[3].find('label').get_text()
    evaluation_read = cols[3].find('a')

    self.evaluated = evaluation != 'Not yet evaluated'
    if evaluation_read:
        self.evaluation_link = evaluation_read['href']
        self.evaluation_read = evaluation_read.get_text() == 'Read'
    
    self.due_date = maybe_date(cols[4].get_text())
    return self

    


def parse_assign(f):
    html = minerva_parser(f)
    rows = html.find('table',{'summary':'List of assignments for this course'}) \
        .find('tbody') \
        .findAll('tr', recursive = False)

    assigns = []
    for row in rows[1:]:
        cols = row.findAll(['th','td'], recursive=False)
        if len(cols) == 1:
            assign = Assign()
            assign.category = True
            assign.name = cols[0].get_text()
        else:
            assign = parse_single(cols)

        assigns.append(assign)

    return formatters.FmtList(assigns)

def dump(shib_credentials,ou):
    data = minerva_get("d2l/lms/dropbox/user/folders_list.d2l?ou=%s&isprv=0" % (ou), base_url=shib_credentials.lms_url)
    return parse_assign(data.text)
