from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import formatters

import re
import json
import dateutil.parser
import datetime

from typing import Optional
from dataclasses import dataclass

"""
Still to do:
1. Viewing feedback
2. Downloading feedback files
3. Downloading assignment attachments
4. Redownloading your own submissions
5. Making submissions
"""



@dataclass
class Assign(formatters.Formattable, formatters.Calendar):
    name:str = ""
    category:bool = False # Is this an assignment or a group of assignments
    submitted:bool= False # Has the student submitted this assignment yet?
    submit_link:str = ""
    evaluated:bool = False # Has this assignment been evaluated yet?
    evaluation_link:str = ""
    evaluation_read:bool = False # Has the evaluation been read?
    due_date:Optional[datetime.datetime] = None # When is the assignment due?
    closed_date:Optional[datetime.datetime] = None # When were submissions closed
    group:Optional[str] = None # The Group of the assignment, if a group assignment
    _ou:Optional[str] = None
    _course:Optional[str] = None
    _lms_url:Optional[str] = None

    def event(self):
        from .formatters import ics
        if not self.due_date:
            return "" # Pointless to generate an event otherwise

        return ics.Event(
                uid=("%s-%s" % (self._ou,deep_clean(self.name))),
                dtstart=self.due_date,
                dtend=self.due_date,
                summary="%s: %s" % (self._course, self.name),
                url="%s%s" % (self._lms_url,self.submit_link)
            )


def deep_clean(text):
    no_weird_chars = re.sub('[^A-Za-z0-9 ]+','',text)
    no_space = no_weird_chars.replace(' ','-')
    no_upper = no_space.lower()
    return no_upper


def maybe_date(text):
    try:
        return dateutil.parser.parse(text,fuzzy=True)
    except ValueError:
        # Actually not a date
        return None

def parse_single(cols,course,lms_url):
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
    self._ou = course.ou 
    self._course = course.course
    self._lms_url = lms_url
    return self

    


def parse_assign(f,course,lms_url):
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
            assign = parse_single(cols,course,lms_url)

        assigns.append(assign)

    return formatters.FmtList(assigns)

def dump(shib_credentials,course):
    data = minerva_get("d2l/lms/dropbox/user/folders_list.d2l?ou=%s&isprv=0" % (course.ou), base_url=shib_credentials.lms_url)
    return parse_assign(data.text,course,shib_credentials.lms_url)
