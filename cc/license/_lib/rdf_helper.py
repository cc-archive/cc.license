import RDF
import datetime
import os

import cc.license
from cc.license._lib.exceptions import RdfHelperError, NoValuesFoundError

# TODO: replace these with RDF.NS objects instead
NS_CC = 'http://creativecommons.org/ns#'
NS_DC = 'http://purl.org/dc/elements/1.1/'
NS_DCQ = 'http://purl.org/dc/terms/'

if os.path.exists('./license.rdf'):
    RDF_PATH = './license.rdf/rdf'
    XML_PATH = './license.rdf/xml'
else:
    BASE_PATH = os.path.dirname(__file__)
    RDF_PATH = os.path.join(BASE_PATH, os.pardir, 'rdf')
    XML_PATH = os.path.join(BASE_PATH, os.pardir, 'xml')
    assert os.path.exists(RDF_PATH)
    assert os.path.exists(XML_PATH)

JURI_RDF_PATH = os.path.join(RDF_PATH, 'jurisdictions.rdf')
INDEX_RDF_PATH = os.path.join(RDF_PATH, 'index.rdf')
SEL_RDF_PATH = os.path.join(RDF_PATH, 'selectors.rdf')
LIC_RDF_PATH = os.path.join(RDF_PATH, 'license_rdf') # directory
# FIXME: Use package.requires for JURI_RDF_PATH

def die_unless(cause, message):
    if cause:
        pass
    else:
        raise RdfHelperError, message

# NOTE: 'object' shadows a global, but fixing it is nontrivial
def query_to_language_value_dict(model, subject, predicate, object):
    """Given a model and a subject, predicate, object (one of which
       is None), generate a dictionary of language values.
       The dictionary is in the form {'en' : u'Germany'}.
       Query is implicitly generated from subject, predicate, object."""
    # Assume either s, p, or o is None
    # so that would be what we want back.
    is_none = [thing for thing in ('subject', 'predicate', 'object')
               if (eval(thing) is None)]
    die_unless( len(is_none) == 1, "You gave me more than one None, " +
                                   "so I don't know what you want back")

    query = RDF.Statement(subject, predicate, object)
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

# NOTE: 'object' shadows a global, but fixing it is nontrivial
def query_to_single_value(model, subject, predicate, object, default = default_flag_value):
    """Much like query_to_language_value_dict, but only returns a single
       value. In fact, raises an exception if the query returns multiple
       values."""
    with_lang = query_to_language_value_dict(model, subject, predicate, object)
    if len(with_lang) > 1:
        raise RdfHelperError, "Somehow I found too many values."
    if len(with_lang) == 1:
        return with_lang.values()[0]
    else: # Nothing to 
        if default is default_flag_value:
            # Then no default was specified
            raise NoValuesFoundError, "No values found."
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

def uri2lang_and_value(uri): # TODO: takes a RDF.Node, not RDF.Url
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

# XXX all get_* helpers below are not directly tested

def get_titles(model, uri):
    """Given a URI for an RDF resource, return a dictionary of
       corresponding to its dc:title properties. The indices will
       be locale codes, and the values will be titles."""
    qstring = """
                     PREFIX dc: <http://purl.org/dc/elements/1.1/>

                     SELECT ?title
                     WHERE
                      {
                         <%s> dc:title ?title .
                      }
                  """
    # get the data back
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    # parse the data
    _titles = {}
    for s in solns:
        tmp = s['title'].literal_value
        _titles[ tmp['language'] ] = tmp['string']
    return _titles

def get_descriptions(model, uri):
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?desc
              WHERE {
                     <%s> dc:description ?desc .
                    }
              """
    # get the data back
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    # parse the data
    if len(solns) == 0:
        return ''
    else:
        _descriptions = {}
        for s in solns:
            tmp = s['desc'].literal_value
            _descriptions[ tmp['language'] ] = tmp['string']
        return _descriptions

def get_version(model, uri):
    qstring = """
              PREFIX dcq: <http://purl.org/dc/terms/>

              SELECT ?version
              WHERE {
                     <%s> dcq:hasVersion ?version .
                    }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    if len(solns) == 0:
        return ''
    else:
        return solns[0]['version'].literal_value['string']

def get_jurisdiction(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?jurisdiction
              WHERE {
                     <%s> cc:jurisdiction ?jurisdiction .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    if len(solns) == 0:
        return cc.license.Jurisdiction('') # empty string makes 'Unported'
    else:
        return cc.license.Jurisdiction(str(solns[0]['jurisdiction'].uri))

def get_deprecated(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
              ASK { <%s> cc:deprecatedOn ?date . }"""
    query = RDF.Query(qstring % uri, query_language='sparql')
    return query.execute(model).get_boolean()

def get_permits(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?permission
              WHERE {
                     <%s> cc:permits ?permission .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return tuple( str(p['permission'].uri) for p in solns )

def get_requires(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?requirement
              WHERE {
                     <%s> cc:requires ?requirement .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return tuple( str(p['requirement'].uri) for p in solns )

def get_superseded(model, uri):
    """Watch out: returns a tuple and not just a value."""
    qstring = """
              PREFIX dcq: <http://purl.org/dc/terms/>

              SELECT ?replacement
              WHERE {
                     <%s> dcq:isReplacedBy ?replacement .
                    }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    if len(solns) == 0:
        return (False, None)
    else:
        superseded_by = str(solns[0]['replacement'].uri)
        return (True, superseded_by)

def get_selector_info():
    """Returns a list of two-tuples holding LicenseSelector information.
       First element is URI, second element is license code (short code)."""
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT ?uri ?lcode
              WHERE {
                     ?uri rdf:type cc:LicenseSelector .
                     ?uri cc:licenseCode ?lcode .
                    }
              """
    query = RDF.Query(qstring, query_language='sparql')
    solns = list(query.execute(SEL_MODEL))
    retval = []
    for s in solns:
        lcode = s['lcode'].literal_value['string']
        uri = str(s['uri'].uri)
        retval.append((uri, lcode))
    return retval


# XXX is this a good idea?
ALL_MODEL = init_model(INDEX_RDF_PATH)
JURI_MODEL = init_model(JURI_RDF_PATH)
SEL_MODEL = init_model(SEL_RDF_PATH)

#####################
## Questions stuff ##
#####################

# The below code will change form eventually, but for now here it is.
from lxml import etree
QUESTION_XML_PATH = os.path.join(XML_PATH, 'questions.xml')

questions_root = etree.parse(QUESTION_XML_PATH).getroot()
