from __future__ import unicode_literals
from __future__ import absolute_import

from .minerva_common import minerva_parser,minerva_get,Frac
from .formatters import FmtList,Formattable
from collections import namedtuple
from typing import List, Union, Optional, Dict, Any, TypeVar,Callable
from dataclasses import dataclass
import re
import json

@dataclass
class Grade(Formattable):
        """ 
        The title of the grade entry
        """
        title:Optional[str]

        """
        True if this is a category of grade items, rather than a single item
        """
        category:bool

        """
        Points achieved, out of the total possible points.
        An entry may be None if it was not recorded in the gradebook.
        """
        points:Optional[Frac]

        """
        System notes, if any, regarding the points (e.g. "Dropped!")
        2scream does not interpret this field, your application should make use of then notes which pertain to it.
        """
        notes:List[str]

        """
        Weight (i.e. portion of the final grade) out of the total possible weight.
        """
        weight:Optional[Frac]

        """
        The grade as recorded in the gradebook. Generally a float, but may be None if not entered, or a string if the instructor entered a non-standard value
        """
        grade:Union[float,str,None]

        """
        Feedback comments as a string.
        """
        feedback:Optional[str]



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

    return colmap

R = TypeVar('R')
V = TypeVar('V')
def call_if_column_value(column_map:Dict[str,Optional[int]], row:List[R], header:str, fn:Callable[[R],V]) -> Optional[V]: 
    column_index = column_map[header]
    if column_index is not None:
        cell:R = row[column_index]
        if s(cell):
            return fn(cell)
    
    return None

            
def with_notes(notes:List[str], fn:Callable[[str], V]) -> Callable[[Any],V]:
    def with_notes_real(notes, fn, cell):
        spans = cell.findAll('span')
        if spans:
            notes.extend(strip_all(spans[1:]))
            return fn(spans[0])
        else:
            return fn(cell)

    return lambda cell: with_notes_real(notes, fn, cell)

def parse_grades(f:str) -> FmtList[Grade]:
    
    def category(row):
        return row.has_attr('class') and 'd_ggl1' in row['class']

    def title(col:Any):
        col = s(col)
        col = col.replace('\n','')
        col = re.sub(' +',' ',col)
        return col

    def grade(col):
        col = s(col).rstrip('%').strip()
        if col == '-':
            return None
        elif col.replace('.','',1).isdigit():  #This is a silly trick to deal with grades with a decimal point
            return float(col)
        else:
            return col

    def feedback(col):
        feedback_individual = col.find('div', {'class': 'd2l-grades-individualcommentlabelcontainer'})
        if feedback_individual:
            inner_div = feedback_individual.find('div')
            if s(inner_div):
                feedback_text = strip_all(inner_div.findAll('div', recursive = False))
                return feedback_text[1]

        # Could be a rubric otherwise, damn it
        return None

    def parse_grade(colmap, row) -> Grade:
        cols = row.findAll(['td','th'],recursive=False)
        cols = unshift_indent(cols)
        if_col = lambda header,fn: call_if_column_value(colmap, cols, header, fn)
           
        notes:List[str] = []
        return Grade(
                title = if_col('Grade Item', title),
                category = category(row),
                points = if_col('Points', with_notes(notes, to_frac)),
                notes = notes,
                weight = if_col('Weight Achieved', with_notes(notes, to_frac)),
                grade = if_col('Grade', grade),
                feedback = if_col('Feedback', feedback)
        )

    html = minerva_parser(f)
    rows = html.find('table', {'summary': 'List of grade items and their values'}).find('tbody',recursive=False).findAll('tr',recursive=False)
    colmap = make_colmap(rows[0].findAll(['th']))

    return FmtList(map(lambda row: parse_grade(colmap,row), rows[1:]))

def dump(shib_credentials,course) -> FmtList[Grade]:
    data = minerva_get("d2l/lms/grades/my_grades/main.d2l?ou=%s" % (course.ou), base_url=shib_credentials.lms_url)
    return parse_grades(data.text)

