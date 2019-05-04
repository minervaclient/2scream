import json
import datetime


def _serializer(x):
    if isinstance(x,datetime.datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return x.__dict__

class Formattable(object):
    def json(self):
        return json.dumps(self, default = _serializer, indent = 2, sort_keys = True)

    def __str__(self):
        return self.json()

class FmtList(Formattable,list):
    def __init__(self,data):
        self.data = data

    def json(self):
        return json.dumps(self.data, default = _serializer, indent = 2, sort_keys = True)
    
    def __str__(self):
        return self.json()
