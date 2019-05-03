
from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import shib_credentials

import re
import json

PARSE_BITS = True

class Course():
    def __init__(self):
        self.ou = None
        self.title = None
        self.term = None
        self.name = None
        self.course = None
        self.internal_code = None


def as_json(objs):
    return json.dumps(objs, default = lambda x: x.__dict__, indent = 2, sort_keys = True)

def to_json(blob):
    blob = re.sub("^while\(1\);","",blob)
    #print blob
    return json.loads(blob)

def parse_courses(blob):
    html = to_json(blob)["Payload"]["Html"]
    html = minerva_parser(html)
    rows = html.find('div',{'id': 'courseSelectorId'}).findAll('li')
    courses = []
    for row in rows:
        links = row.findAll('a')
        content = None
        for link in links:
            if link['href'].startswith('/d2l/home/'):
                content = link
                break

        course = Course()
        course.ou = link['href'].replace("/d2l/home/","")
        course.title = link.get_text()
        
        if PARSE_BITS == True:
            title = link.get_text().split(" - ")
            course.term = title[0]
            course.course = title[1]
            course.internal_code = title[-1]
            if len(title) == 4:
                course.name = title[2]

        courses.append(course)
    return courses
            

    

def dump_courses():
    data = minerva_get("d2l/lp/courseSelector/%s/InitPartial?_d2l_prc$headingLevel=2&_d2l_prc$scope=&_d2l_prc$hasActiveForm=false&isXhr=true&requestId=2" % ("6606"), base_url=shib_credentials.lms_url)
    return parse_courses(data.text)

