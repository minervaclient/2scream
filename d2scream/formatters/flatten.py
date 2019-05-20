import typing
from d2scream.minerva_common import FuckingNamedTuple


def is_namedtuple(obj):
    if not isinstance(obj,type):
        return False

    return issubclass(obj,FuckingNamedTuple)

def get_tuple_type(annot):
        if type(annot) == typing._GenericAlias:
            valtype = annot.__args__[0]
            if  is_namedtuple(valtype):
                return valtype,True
        elif is_namedtuple(annot):
            return annot, False
        
        return None, False

def flatten_keys(obj,prefix=''):
    fields = []
    prefix = prefix + '_' if prefix else ''
    for key, annot in obj.__annotations__.items():
        tuple_type,_ = get_tuple_type(annot)
        if tuple_type:
            fields.extend(flatten_keys(tuple_type,prefix=prefix + key))
        else:
            fields.append(prefix  + key)
    return fields


def flatten_sql_schema(obj,prefix='',nullable=False):
    def sql_field(name, annot, force_nullable):
        if type(annot) == typing._GenericAlias:
            if len(annot.__args__) == 2 and annot.__args__[1] == type(None):
                annot = annot.__args__[0]
                force_nullable = True

        if annot == bool or annot == int:
            coltype = "INTEGER"
        elif annot == float:
            coltype = "REAL"
        else:
            coltype = "TEXT"

        null_wording = "NULL" if force_nullable else "NOT NULL"
        return "%s %s %s" % (name, coltype, null_wording)

    fields = []
    prefix = prefix + '_' if prefix else ''
    for key, annot in obj.__annotations__.items():
        tuple_type, tuple_nullable = get_tuple_type(annot)
        if tuple_type:
            fields.extend(flatten_sql_schema(tuple_type, prefix = prefix + key, nullable = tuple_nullable))
        else:
            fields.append(sql_field(prefix + key, annot,  nullable))
    return fields


def flatten_values(obj,prefix=''):
    vals = {}
    prefix = prefix + '_' if prefix else ''
    for key, annot in obj.__annotations__.items():
        tuple_type,_ = get_tuple_type(annot)
        if tuple_type:
            vals.update(flatten_values(tuple_type,prefix = prefix + key))
        else:
            if hasattr(obj, key):
                vals[prefix + key] = getattr(obj,key)
            else:
                vals[prefix + key] = None
    return vals
