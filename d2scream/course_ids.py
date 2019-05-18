
from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import formatters

import re
import json
from dataclasses import dataclass
from typing import Optional,Any

PARSE_BITS = True

@dataclass
class Course(formatters.Formattable):
    """
    The internal identifier for a course,
    which must be used in further requests pertaining to that course.
    """
    ou:Any

    """
    The complete title of a course as it appears in the LMS
    e.g. "Fall 2019 - COMP 330 - Theory of Computation - CKC.304904"
    """
    full_title:str

    """
    For universities where this may be determined, the term of the course
    """
    term:Optional[str] = None

    """
    For universities where this may be determined, the name of the course
    e.g. "Theory of Computation"
    """
    name:Optional[str] = None

    """
    For universities where this may be determined, the code of the course,
    which generally may be used to make requests to other systems about the same course
    """
    course:Optional[str] = None

    """
    The meaning of this field is unknown. It is offered for your confusion.
    """
    internal_code:Optional[str] = None



def to_json(blob):
    blob = re.sub("^while\(1\);","",blob)
    return json.loads(blob)

def parse_courses(blob:str) -> formatters.FmtList[Course]:
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

        course = Course(
                ou = link['href'].replace("/d2l/home/",""),
                full_title = link.get_text()
        )
        
        if PARSE_BITS == True:
            title = course.full_title.split(" - ")
            course.term = title[0]
            course.course = title[1]
            course.internal_code = title[-1]
            if len(title) == 4:
                course.name = title[2]

        courses.append(course)
    return formatters.FmtList(courses)
            

    

def dump(shib_credentials) -> formatters.FmtList[Course]:
    data = minerva_get("d2l/lp/courseSelector/%s/InitPartial?_d2l_prc$headingLevel=2&_d2l_prc$scope=&_d2l_prc$hasActiveForm=false&isXhr=true&requestId=2" % ("6606"), base_url=shib_credentials.lms_url)
    return parse_courses(data.text)
