import RDF
import datetime

NS_CC='http://creativecommons.org/ns#'
NS_DC='http://purl.org/dc/elements/1.1/'
NS_DCQ='http://purl.org/dc/terms/'
JURI_RDF_PATH='./license.rdf/rdf/jurisdictions.rdf'
LIC_RDF_PATH ='./license.rdf/license_rdf/'
# FIXME: Use package.requires for JURI_RDF_PATH

class RdfHelperException(Exception):
    pass

class NoValuesFoundException(RdfHelperException):
    pass

def die_unless(cause, message):
    if cause:
        pass
    else:
        raise RdfHelperException, message

def query_to_language_value_dict(model, subject, predicate, obj):
    """Given a model and a subject, predicate, object (one of which
       is None), generate a dictionary of language values.
       The dictionary is in the form {'en' : u'Germany'}.
       Query is implicitly generated from subject, predicate, object."""
    # Assume either s, p, or o is None
    # so that would be what we want back.
    is_none = [thing for thing in ('subject', 'predicate', 'obj')
               if (eval(thing) is None)]
    die_unless( len(is_none) == 1, "You gave me more than one None, " +
                                   "so I don't know what you want back")

    query = RDF.Statement(subject, predicate, obj)
    results = list(model.find_statements(query))

    interesting_ones = [getattr(result, is_none[0]) for result in results]
    values_with_lang = [uri2lang_and_value(result) for result in interesting_ones]

    # Now, collapse this into a dict, ensuring there are no duplicate keys
    ret = {}
    for (lang, val) in values_with_lang:
        die_unless( lang not in ret, "Duplicate language found; blowing up")
        ret[lang] = val
    return ret

default_flag_value = object() # TODO: ask asheesh why this is here

def query_to_single_value(model, subject, predicate, obj, default = default_flag_value):
    """Much like query_to_language_value_dict, but only returns a single
       value. In fact, raises an exception if the query returns multiple
       values."""
    with_lang = query_to_language_value_dict(model, subject, predicate, obj)
    if len(with_lang) > 1:
        raise RdfHelperException, "Somehow I found too many values."
    if len(with_lang) == 1:
        return with_lang.values()[0]
    else: # Nothing to 
        if default is default_flag_value:
            # Then no default was specified
            raise NoValuesFoundException, "No values found."
        else:
            return default

def to_date(s):
    return datetime.date(*map(int, s.split('-')))

def to_bool(s):
    s = s.lower()
    die_unless( s in ('true', 'false'), "Non-bool found in literal; blowing up")
    return {'true': True, 'false': False}[s]

type2converter = {
    'http://www.w3.org/2001/XMLSchema-datatypes#boolean': to_bool,
    'http://www.w3.org/2001/XMLSchema-datatypes#date': to_date,
}

def uri2lang_and_value(uri):
    if uri.type == 1: # Is there a list of these somewhere?
        # a URI
        return (None, str(uri.uri))
    if uri.type == 2: # TODO: fix magic number
        # It's a literal - but what kind?
        literal = uri.literal_value
        strvalue = uri.literal_value['string']
        type = literal['datatype']
        type = str(type)
        return (literal['language'], type2converter.get(type, lambda thing: thing)(strvalue))
    raise "uri.type contains unknown constant"

def uri2value(uri):
    return uri2lang_and_value(uri)[1]

def init_model(*filenames):
    """Input: A list of on-disk paths (filenames) to start from.
       Output: A model with those suckers parsed."""
    for filename in filenames: # filenames, not URIs
        die_unless(':/' not in filename, "You passed in something that " +
                                         "looks like a URI; blowing up")

    storage = RDF.Storage(storage_name="hashes",
                          name="test",
                          options_string="new='yes',hash-type='memory',dir='.'")
    if storage is None:
        raise "new RDF.Storage failed"

    model = RDF.Model(storage)
    if model is None:
        raise "new RDF.Model failed"

    parser = RDF.Parser('raptor')
    for filename in filenames:
        filename_uri = RDF.Uri(string="file:" + filename)
        parser.parse_into_model(model, filename_uri)
    return model

