from __future__ import absolute_import
from __future__ import unicode_literals

import json
import datetime
import csv
import io
import collections
import pprint
from typing import TypeVar, List
from . import flatten

class Formattable(object):
    def json(self):
        return json.dumps(self, default = _serializer, indent = 2, sort_keys = True)

    def csv(self):
        stringio = io.StringIO()
        writer = csv.DictWriter(stringio, flatten.flatten_keys(self))
        writer.writeheader()
        writer.writerow(flatten.flatten_values(self))
        return stringio.getvalue()

    def yaml(self, human = True):
        import yaml
        if human:
            yaml.add_multi_representer(list,yaml.representer.SafeRepresenter.represent_list)
            yaml.add_multi_representer(tuple,yaml.representer.SafeRepresenter.represent_list)
        return yaml.dump(self)

    def sql(self):
        cls = self.__class__.__name__.lower()
        return _sql_insert(cls,[self])

    def __str__(self):
        return pprint.pformat(self)

class Calendar(object):
    def ics(self):
        return self.event().dump()

T = TypeVar('T')
class FmtList(Formattable,List[T]):
    def csv(self):
        stringio = io.StringIO()
        writer = csv.DictWriter(stringio, flatten.flatten_keys(self[0]))
        writer.writeheader()
        writer.writerows(flatten.flatten_values(item) for item in self)
        return stringio.getvalue()


    def sql(self):
        cls = self[0].__class__.__name__.lower()
        text = 'CREATE TABLE IF NOT EXISTS "%s" (%s);\n' % (cls,  ", ".join(flatten.flatten_sql_schema(self[0])))
        text += _sql_insert(cls,self)
        return text

    def ics(self):
        from .ics import Calendar
        events = filter(lambda event: event, [obj.event() for obj in self])
        return Calendar(events).dump()

    def __str__(self):
        return pprint.pformat(self)


def _serializer(x):
    if isinstance(x,datetime.datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return x.__dict__

def _sql_insert(table,rows):
        def sql_repr(v):
            if v is None:
                return "null"
            if v == True:
                return "1"
            if v == False:
                return "0"
            if isinstance(v,list):
                return "'%s'" % (repr(v))
            if isinstance(v,datetime.datetime):
                return repr(v.strftime("%Y-%m-%dT%H:%M:%S"))

            return repr(v)

        sql_rows = []
        for row in rows:
            row = flatten.flatten_values(row)
            row = ", ".join([sql_repr(col) for col in row.values()])
            row = "(%s)" % (row)
            sql_rows.append(row)

        values = ",\n".join(sql_rows)
        return "INSERT INTO %s VALUES %s;" % (table, values)
