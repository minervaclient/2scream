from __future__ import absolute_import
from __future__ import unicode_literals

from .minerva_common import *
from . import formatters
from collections import namedtuple

import re
import json

class Grade(formatters.Formattable):
    def __init__(self):
        """
        title:str option 
        The title as it appears in the gradebook.
        """
        self.title = None

        """
        category:bool
        True if this is a category of grade items, rather than a particular assessment
        """
        self.category = False

        """
        points:float option*float option 
        Points achieved, out of the total possible points.
        An entry may be None if it was not recorded in the gradebook.
        """
        self.points = Frac(0.0,0.0)

        """
        notes:str list option 
        System notes, if any, regarding the points (e.g. "Dropped!")
        2scream does not interpret this field, your application should make use of then notes which pertain to it.
        """
        self.notes = []

        """
        weight: float * float
        Weight (i.e. portion of the final grade) out of the total possible weight.
        """
        self.weight = Frac(0.0,0.0)

        """
        grade: any
        The grade as recorded in the gradebook. Generally a float, but may be None if not entered, or a string if the instructor entered a non-standard value
        """
        self.grade = None

        """
        feedback: str option
        Feedback comments as a string.
        """
        self.feedback = None

    def __repr__(self):
        return self.__dict__.__repr__()
    
    

    
    


def strip_all(elms):
    return [elm.getText('\n').strip() for elm in elms if elm.getText().strip() != ""]

def s(elm):
    if elm is None: return None
    return elm.get_text('\n').strip() if elm.get_text().strip() != "" else None


def unshift_indent(texts):
    while texts[0].get_text().strip() == "":
        texts.pop(0)
    return texts

def to_float(text):
    if text != '-':
        return float(text)
    else:
        return None

def to_frac(text):
    text = s(text)
    if text.endswith('%'):
        return Frac(to_float(text.rstrip('%').strip()),100.0)
    else:
        p = text.split(' / ')
        if len(p) == 2:
            return Frac(to_float(p[0]),to_float(p[1]))
        else:
            # This is really dodgy, but ok
            return Frac(to_float(p[0]),1.0)


def make_colmap(cols):
    colmap = {
        'Grade Item': None,
        'Points': None,
        'Weight Achieved': None,
        'Grade': None,
        'Feedback': None
    }

    for i,col in enumerate(cols):
        colmap[s(col)] = i

    return lambda row, col: row[colmap[col]] if colmap[col] is not None else None

def parse_grades(f):
    html = minerva_parser(f)
    rows = html.find('table', {'summary': 'List of grade items and their values'}).find('tbody',recursive=False).findAll('tr',recursive=False)
    gradebook = []
    get = make_colmap(rows[0].findAll(['th']))

    for row in rows[1:]:
        struct = Grade()
        if row.has_attr('class') and 'd_ggl1' in row['class']:
            struct.category = True
        else: 
            struct.category = False

        cols = row.findAll(['td','th'],recursive=False)
        cols = unshift_indent(cols)
        
        if s(get(cols,'Grade Item')):
            struct.title = s(get(cols,'Grade Item'))
            struct.title = struct.title.replace('\n','')
            struct.title = re.sub('  +',' ',struct.title)
        if s(get(cols,'Points')): 
            spans = get(cols,'Points').findAll('span')

            if spans:
                actual_points = spans[0]
                struct.notes = strip_all(spans[1:])
            else:
                actual_points = get(cols,'Points')

            struct.points =  to_frac(actual_points)


        if s(get(cols,'Weight Achieved')):
            spans = get(cols,'Weight Achieved').findAll('span')

            if spans:
                actual_weight = spans[0]
                struct.notes = strip_all(spans[1:])
            else:
                actual_weight = get(cols,'Weight Achieved')

            struct.weight = to_frac(actual_weight)
        
        if s(get(cols,'Grade')):
            grade = s(get(cols,'Grade')).rstrip('%').strip()
            if grade == '-':
                grade = None
            elif grade.replace('.','',1).isdigit(): #This is a silly trick to deal with grades with a decimal point
                grade = float(grade)
            else:
                pass # Leave the unfiltered grade

            struct.grade = grade


        if s(get(cols,'Feedback')):
            feedback_individual = get(cols,'Feedback').find('div', {'class': 'd2l-grades-individualcommentlabelcontainer'})
            if feedback_individual:
                inner_div = feedback_individual.find('div')
                if s(inner_div):
                    feedback = strip_all(inner_div.findAll('div', recursive = False))
                    struct.feedback = feedback[1]
                # Could be a rubric otherwise, damn it


        gradebook.append(struct)

    return formatters.FmtList(gradebook)

def dump(shib_credentials,ou):
    data = minerva_get("d2l/lms/grades/my_grades/main.d2l?ou=%s" % (ou), base_url=shib_credentials.lms_url)
    return parse_grades(data.text)

