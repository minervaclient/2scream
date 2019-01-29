from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import shib_credentials

import re
import json

class Grade(object):
    """
    title:str option 
    The title as it appears in the gradebook.
    """
    title = None

    """
    category:bool
    True if this is a category of grade items, rather than a particular assessment
    """
    category = False

    """
    points:float option*float option 
    Points achieved, out of the total possible points.
    An entry may be None if it was not recorded in the gradebook.
    """
    points = (None,None)

    """
    notes:str list option 
    System notes, if any, regarding the points (e.g. "Dropped!")
    2scream does not interpret this field, your application should make use of then notes which pertain to it.
    """
    notes = []

    """
    weight: float * float
    Weight (i.e. portion of the final grade) out of the total possible weight.
    """
    weight = (0.0,0.0)

    """
    grade: any
    The grade as recorded in the gradebook. Generally a float, but may be None if not entered, or a string if the instructor entered a non-standard value
    """
    grade = None

    """
    feedback: str option
    Feedback comments as a string.
    """
    feedback = None

    def __repr__(self):
        return self.__dict__.__repr__()
    
    

    
    


def strip_all(elms):
    return [elm.getText('\n').strip() for elm in elms if elm.getText().strip() != ""]

def s(elm):
    return elm.get_text('\n').strip() if elm.get_text().strip() != "" else None


def unshift_indent(texts):
    while texts[0].get_text().strip() == "":
        texts.pop(0)
    return texts


def as_json(objs):
    return json.dumps(objs, default = lambda x: x.__dict__, indent = 2, sort_keys = True)

def dump_grades(f):
    html = minerva_parser(f)
    rows = html.find('table', {'summary': 'List of grade items and their values'}).findAll('tr')
    gradebook = []
    for row in rows[1:]:
        struct = Grade()
        if row.has_attr('class') and 'd_ggl1' in row['class']:
            struct.category = True
        else: 
            struct.category = False

        cols = row.findAll(['td','th'])
        cols = unshift_indent(cols)
        
        if s(cols[0]):
            struct.title = s(cols[0])

        if s(cols[1]): 
            spans = cols[1].findAll('span')

            if spans:
                actual_points = spans[0]
                struct.notes = strip_all(spans[1:])
            else:
                actual_points = cols[1]

            points = s(actual_points).split(' / ')

            struct.points =  tuple(float(p) if p != '-' else None for p in points)


        if s(cols[2]):
            struct.weight = tuple(float(n) for n in s(cols[2]).split(' / '))
        
        if s(cols[3]):
            grade = s(cols[3]).rstrip('%').strip()
            if grade == '-':
                grade = None
            elif grade.isdigit():
                grade = float(grade)
            else:
                grade = None

            struct.grade = grade


        if s(cols[4]):
            inner_div = cols[4].find('div', {'class': 'd2l-grades-individualcommentlabelcontainer'}).find('div')
            if s(inner_div):
                feedback = strip_all(inner_div.findAll('div', recursive = False))
                struct.feedback = feedback[1]


        gradebook.append(struct)

    return gradebook

