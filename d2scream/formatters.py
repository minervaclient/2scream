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

    
class Formattable(object):
    def json(self):
        return json.dumps(self, default = _serializer, indent = 2, sort_keys = True)

    def csv(self):
        s = io.StringIO()
        writer = csv.DictWriter(s,next(_flatten_tuple([self])))
        writer.writerows(_flatten_tuple([self]))
        s.seek(0)
        return s.read()

    def yaml(self, human = True):
        import yaml
        if human:
            yaml.add_multi_representer(list,yaml.representer.SafeRepresenter.represent_list)
            yaml.add_multi_representer(tuple,yaml.representer.SafeRepresenter.represent_list)
        return yaml.dump(self)
        
 
    def __str__(self):
        return pprint.pformat(self)

class FmtList(Formattable,list):
    def csv(self):
        s = io.StringIO()
        writer = csv.DictWriter(s,next(_flatten_tuple(self)))
        writer.writeheader()
        writer.writerows(_flatten_tuple(self))
        s.seek(0)
        return s.read()

    def __str__(self):
        return pprint.pformat(self)

