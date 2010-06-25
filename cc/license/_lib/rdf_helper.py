import pkg_resources

import RDF
import datetime

import cc.license
from cc.license._lib.exceptions import RdfHelperError, NoValuesFoundError

# TODO: replace these with RDF.NS objects instead
NS_CC = 'http://creativecommons.org/ns#'
NS_DC = 'http://purl.org/dc/elements/1.1/'
NS_DCQ = 'http://purl.org/dc/terms/'

JURI_RDF_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'rdf/jurisdictions.rdf')
INDEX_RDF_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'rdf/index.rdf')
SEL_RDF_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'rdf/selectors.rdf')
LIC_RDF_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'rdf/license_rdf') # directory
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
    """Input: An on-disk path (filenames) to start from.
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

def get_prohibits(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?prohibition
              WHERE {
                     <%s> cc:prohibits ?prohibition .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return tuple( str(p['prohibition'].uri) for p in solns )

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

def get_selector_uris():
    """Returns a list of LicenseSelector URIs."""
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT ?uri
              WHERE {
                     ?uri rdf:type cc:LicenseSelector .
                    }
              """
    query = RDF.Query(qstring, query_language='sparql')
    solns = list(query.execute(SEL_MODEL))
    return [ str(s['uri'].uri) for s in solns ]

def get_selector_id(uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?lcode
              WHERE {
                     <%s> cc:licenseCode ?lcode .
                    }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(SEL_MODEL))
    return str(solns[0]['lcode'].literal_value['string'])

def get_license_uris(model, selector_uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT ?luri
              WHERE {
                     ?luri rdf:type cc:License .
                     ?luri cc:licenseClass <%s> .
                    }
              """
    query = RDF.Query(qstring % selector_uri, query_language='sparql')
    solns = list(query.execute(model))
    return tuple( str(s['luri'].uri) for s in solns )


def get_license_code(model, uri):
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?code
              WHERE {
                     <%s> dc:identifier ?code .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return str(solns[0]['code'].literal_value['string'])

def get_license_class(model, uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?lclassuri
              WHERE {
                     <%s> cc:licenseClass ?lclassuri .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return str(solns[0]['lclassuri'].uri)

def get_logos(model, uri):
    qstring = """
              PREFIX foaf: <http://xmlns.com/foaf/0.1/>

              SELECT ?img
              WHERE {
                     <%s> foaf:logo ?img .
              }
              """
    query = RDF.Query(qstring % uri, query_language='sparql')
    solns = list(query.execute(model))
    return tuple( str(s['img'].uri) for s in solns )


def selector_has_license(model, selector_uri, license_uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              ASK { <%s> cc:licenseClass <%s> . }"""
    # can't interpolate empty strings
    if selector_uri == '':
        selector_uri =  'NONE'
    if license_uri == '':
        license_uri = 'NONE'
    query = RDF.Query(qstring % (license_uri, selector_uri),
                      query_language='sparql')
    return query.execute(model).get_boolean()

def get_jurisdiction_default_language(juris_uri):
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?default_language
              WHERE {
                     <%s> cc:defaultLanguage ?default_language
                    }
              """
    query = RDF.Query(qstring % juris_uri, query_language='sparql')
    results = [
        str(result['default_language'])
        for result in query.execute(JURI_MODEL)]
    if results:
        return results[0]
    else:
        return None

# XXX is this a good idea?
ALL_MODEL = init_model(INDEX_RDF_PATH)
JURI_MODEL = init_model(JURI_RDF_PATH)
SEL_MODEL = init_model(SEL_RDF_PATH)

#####################
## Questions stuff ##
#####################

# The below code will change form eventually, but for now here it is.
from lxml import etree
QUESTION_XML_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'xml/questions.xml')

questions_root = etree.parse(QUESTION_XML_PATH).getroot()
