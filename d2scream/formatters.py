from __future__ import absolute_import
from __future__ import unicode_literals

import json
import datetime
import csv
import io
import collections
import pprint


def _serializer(x):
    if isinstance(x,datetime.datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return x.__dict__

def _flatten_tuple(lst):
    for row in lst:
        d = dict(row.__dict__)
        for k in list(d.keys()):
            if isinstance(d[k],tuple):
                for kk,vv in d[k]._asdict().items():
                    d["%s_%s" % (k,kk)] = vv

                del d[k]

        yield d

def _sql_create(table, keys):
    def sql_type(v):
        if isinstance(v,int):
            return "int"
        if isinstance(v,float):
            return "real"
        
        return "text"

    sql_keys = [ "\"%s\" %s" % (key, sql_type(sample)) for key,sample in keys.items()]
    sql_keys = ", ".join(sql_keys)
    return "CREATE TABLE IF NOT EXISTS %s (%s);" % (table, sql_keys)

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
            row = ", ".join([sql_repr(col) for col in row.values()])
            row = "(%s)" % (row)
            sql_rows.append(row)
        
        values = ",\n".join(sql_rows)
        return "INSERT INTO %s VALUES %s;" % (table, values)
    
class Formattable(object):
    def json(self):
        return json.dumps(self, default = _serializer, indent = 2, sort_keys = True)

    def csv(self):
        s = io.StringIO()
        writer = csv.DictWriter(s,next(_flatten_tuple([self])))
        writer.writerows(_flatten_tuple([self]))
        s.seek(0)
        return s.getvalue()

    def yaml(self, human = True):
        import yaml
        if human:
            yaml.add_multi_representer(list,yaml.representer.SafeRepresenter.represent_list)
            yaml.add_multi_representer(tuple,yaml.representer.SafeRepresenter.represent_list)
        return yaml.dump(self)

    def sql(self):
        return _sql_insert(self.__class__.__name__.lower(), _flatten_tuple([self]))
 
    def __str__(self):
        return pprint.pformat(self)

class FmtList(Formattable,list):
    def csv(self):
        s = io.StringIO()
        writer = csv.DictWriter(s,next(_flatten_tuple(self)))
        writer.writeheader()
        writer.writerows(_flatten_tuple(self))
        s.seek(0)
        return s.getvalue()


    def sql(self):
        cls = self[0].__class__.__name__.lower()
        create = _sql_create(cls,next(_flatten_tuple(self)))
        ins = _sql_insert(cls, _flatten_tuple(self))
        return "%s\n%s" % (create,ins)

    def __str__(self):
        return pprint.pformat(self)

