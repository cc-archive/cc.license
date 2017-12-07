from builtins import map
from builtins import str

import pkg_resources

from rdflib import Graph
from pyparsing import ParseException
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
        raise RdfHelperError(message)

def init_model(filename):
    """Input: An on-disk filename to start from.
       Output: A parsed graph."""
    die_unless(':/' not in filename, "You passed in something that " +
               "looks like a URI; blowing up")
    g = Graph()
    return g.parse(filename, format='xml')

ALL_MODEL = init_model(INDEX_RDF_PATH)
JURI_MODEL = init_model(JURI_RDF_PATH)
SEL_MODEL = init_model(SEL_RDF_PATH)


def query_to_language_value_dict(rdf_subject, rdf_predicate, rdf_object,
                                 model=False):
    """Given a model and a subject, predicate, object (one of which
       is None), generate a dictionary of language values.
       The dictionary is in the form {'en' : u'Germany'}.
       Query is implicitly generated from subject, predicate, object."""
    if model == False:
        model = JURI_MODEL
    # Make sure only one is specified as None
    die_unless( sum(x is None for x in [rdf_subject,
                                        rdf_predicate,
                                        rdf_object]) == 1,
                "You gave me more than one None, " +
                "so I don't know what you want back")
    # Get the index of the wanted item, specified as None
    wanted = 0 if rdf_subject != None else 1 if rdf_predicate != None else 2
    results = model.triples( (rdf_subject, rdf_predicate, rdf_object) )
    # list of
    interesting_ones = [result[wanted] for result in results]
    #FIXME!!!!: We *never* get languages at the moment
    values_with_lang = [uri2lang_and_value(result)
                        for result in interesting_ones]

    # Now, collapse this into a dict, ensuring there are no duplicate keys
    ret = {}
    for (lang, val) in values_with_lang:
        die_unless( lang not in ret, "Duplicate language found; blowing up")
        ret[lang] = val
    return ret

default_flag_value = object() # TODO: ask asheesh why this is here

# NOTE: 'object' shadows a global, but fixing it is nontrivial
def query_to_single_value(rdf_subject, rdf_predicate, rdf_object,
                          default=default_flag_value,
                          model=False):
    """Much like query_to_language_value_dict, but only returns a single
       value. In fact, raises an exception if the query returns multiple
       values."""

    if model == False:
        model = JURI_MODEL

    with_lang = query_to_language_value_dict(rdf_subject, rdf_predicate,
                                             rdf_object, model)
    if len(with_lang) > 1:
        raise RdfHelperError("Somehow I found too many values.")
    if len(with_lang) == 1:
        return list(with_lang.values())[0]
    else: # Nothing to 
        if default is default_flag_value:
            # Then no default was specified
            raise NoValuesFoundError("No values found.")
        else:
            return default

def to_date(s):
    return datetime.date(*list(map(int, s.split('-'))))

def to_bool(s):
    s = s.lower()
    die_unless( s in ('true', 'false'), "Non-bool found in literal; blowing up")
    return {'true': True, 'false': False}[s]

type2converter = {
    'http://www.w3.org/2001/XMLSchema-datatypes#boolean': to_bool,
    'http://www.w3.org/2001/XMLSchema-datatypes#date': to_date,
}

def uri2lang_and_value(uri):
    #return(uri['language'], str(uri))
    return(None, str(uri))

def uri2value(uri):
    return uri2lang_and_value(uri)[1]


# XXX all get_* helpers below are not directly tested

def get_titles(uri, model=False):
    """Given a URI for an RDF resource, return a dictionary of
       corresponding to its dc:title properties. The indices will
       be locale codes, and the values will be titles."""
    if model == False:
        model = ALL_MODEL
    qstring = """
                     PREFIX dc: <http://purl.org/dc/elements/1.1/>

                     SELECT ?title
                     WHERE
                      {
                         <%s> dc:title ?title .
                      }
                  """
    # get the data back
    results = model.query(qstring % uri)
    # parse the data
    _titles = {}
    for s in results:
        tmp = s['title']
        _titles[ tmp.language ] = tmp.value
    return _titles

def get_descriptions(uri, model=False):
    # Fixme: This function isn't hit by any tests.
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?desc
              WHERE {
                     <%s> dc:description ?desc .
                    }
              """

    # get the data back
    solns = model.query(qstring % uri)
    # parse the data
    if len(solns) == 0:
        return ''
    else:
        _descriptions = {}
        for s in solns:
            tmp = s['desc']
            _descriptions[ tmp.language ] = tmp.value
        return _descriptions

def get_version(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX dcq: <http://purl.org/dc/terms/>

              SELECT ?version
              WHERE {
                     <%s> dcq:hasVersion ?version .
                    }
              """
    solns = model.query(qstring % uri)
    if len(solns) == 0:
        return ''
    else:
        # Just get the first one
        for soln in solns:
            return soln['version'].value

def get_jurisdiction(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?jurisdiction
              WHERE {
                     <%s> cc:jurisdiction ?jurisdiction .
              }
              """

    solns = model.query(qstring % uri)
    if len(solns) == 0:
        return cc.license.Jurisdiction('') # empty string makes 'Unported'
    else:
        # Just get the first one
        for soln in solns:
            return cc.license.Jurisdiction(str(soln['jurisdiction']))

'''
def get_unported_license_uris(model):

    So this SPARQL query requires librdf > 1.0.10 which is not
    available in debian stable as of 07/2010. When `squeeze` is
    released, and a new version of librdf can be safely installed,
    then we can use the query below and eliminate the python hackery.

    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT ?luri
              WHERE {
                     ?luri rdf:type cc:License .
                     OPTIONAL { ?luri cc:jurisdiction ?juri .} .
                     FILTER (!BOUND(?juri))
              }
              """
    solns = model.query(qstring)
    return tuple(str(s['luri']) for s in solns)
'''

def get_jurisdiction_licenses(uri, model=False):
    if model == False:
        model = ALL_MODEL
    # FIXME: This function is never hit by any unit tests.
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?license
              WHERE {
                     ?license cc:jurisdiction <%s> .
              }
              """
    solns = model.query(qstring % uri)
    if len(solns) == 0:
        return [] # empty makes 'Unported'
    else:
        return [str( l['license'] ) for l in solns]

def get_deprecated(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              
              ASK { <%s> cc:deprecatedOn ?date . }
              """
    result = model.query(qstring % uri)
    return result

def get_permits(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?permission
              WHERE {
                     <%s> cc:permits ?permission .
              }
              """
    permits = model.query(qstring % uri)
    return tuple(str(p['permission']) for p in permits)

def get_requires(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?requirement
              WHERE {
                     <%s> cc:requires ?requirement .
              }
              """
    requires = model.query(qstring % uri)
    return tuple(str(p['requirement']) for p in requires)

def get_prohibits(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?prohibition
              WHERE {
                     <%s> cc:prohibits ?prohibition .
              }
              """
    prohibits = model.query(qstring % uri)
    return tuple(str(p['prohibition']) for p in prohibits)

def get_superseded(uri, model=False):
    if model == False:
        model = ALL_MODEL
    """Watch out: returns a tuple and not just a value."""
    qstring = """
              PREFIX dcq: <http://purl.org/dc/terms/>

              SELECT ?replacement
              WHERE {
                     <%s> dcq:isReplacedBy ?replacement .
                    }
              """
    solns = model.query(qstring % uri)
    if len(solns) == 0:
        return (False, None)
    else:
        # Just get the first one
        for soln in solns:
            superseded_by = str(soln['replacement'])
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
    selector_uris = SEL_MODEL.query(qstring)
    return [str(s[0]) for s in selector_uris]

def get_selector_id(uri):
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?lcode
              WHERE {
                     <%s> cc:licenseCode ?lcode .
                    }
              """
    solns = SEL_MODEL.query(qstring % uri)
    # Just get the first item
    for soln in solns:
        return str(soln[0])

def get_license_uris(selector_uri, model=False):
    if model == False:
        model = ALL_MODEL
    # FIXME: This function is never hit by any unit tests.
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT ?luri
              WHERE {
                     ?luri cc:licenseClass <%s> .
                    }
              """
    solns = model.query(qstring % selector_uri)
    return tuple(str(s[0]) for s in solns)


def get_license_code(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?code
              WHERE {
                     <%s> dc:identifier ?code .
              }
              """
    solns = model.query(qstring % uri)
    # Just get the first item
    for soln in solns:
        return str(soln['code'].value)

def get_license_class(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?lclassuri
              WHERE {
                     <%s> cc:licenseClass ?lclassuri .
              }
              """
    solns = model.query(qstring % uri)
    # Just get the first item
    for soln in solns:
        return str(soln['lclassuri'])

def get_logos(uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX foaf: <http://xmlns.com/foaf/0.1/>

              SELECT ?img
              WHERE {
                     <%s> foaf:logo ?img .
              }
              """
    solns = model.query(qstring % uri)
    return tuple(str(s['img']) for s in solns)


def selector_has_license(selector_uri, license_uri, model=False):
    if model == False:
        model = ALL_MODEL
    qstring = """
              PREFIX cc: <http://creativecommons.org/ns#>

              ASK { <%s> cc:licenseClass <%s> . }"""
    # can't interpolate empty strings
    if selector_uri == '':
        selector_uri =  'NONE'
    if license_uri == '':
        license_uri = 'NONE'
    # If the selector is badly specified this will raise a ParseException
    # In this circumstance the existing code does not expect an exception,
    # so we return False.
    try:
        soln = model.query(qstring % (license_uri, selector_uri))
        has = bool(soln)
    except ParseException:
        has = False
    return has


def get_jurisdiction_default_language(juris_uri):
    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>
              PREFIX cc: <http://creativecommons.org/ns#>

              SELECT ?default_language
              WHERE {
                     <%s> cc:defaultLanguage ?default_language
                    }
              """
    languages = JURI_MODEL.query(qstring % juris_uri)
    results = [
        str(result['default_language'])
        for result in languages]
    if results:
        return results[0]
    else:
        return None

JURISDICTIONS_FOR_SELECTOR_CACHE = {}
def jurisdictions_for_selector(selector_uri):
    """
    Find out all the jurisdictions relevant to a selector/licenseclass

    That is, find all the unique jurisdictions that licenses in this
    selector have.

    Returns:
      A list of jurisdiction URIs
    """
    if selector_uri in JURISDICTIONS_FOR_SELECTOR_CACHE:
        return JURISDICTIONS_FOR_SELECTOR_CACHE[selector_uri]

    qstring = """
       PREFIX cc: <http://creativecommons.org/ns#>

       SELECT ?jurisdiction
       WHERE {
         ?license cc:licenseClass <%s> .
         ?license cc:jurisdiction ?jurisdiction . }"""
    jurisdictions = ALL_MODEL.query(qstring % selector_uri)
    results = set(
        [str(result[0])
         for result in jurisdictions])

    JURISDICTIONS_FOR_SELECTOR_CACHE[selector_uri] = results

    return results


def get_license_legalcodes(license_uri):
    """
    Return a list of [(legalcode_uri, legalcode_lang)] for license_uri

    If this is a single-legalcode option, it'll probably return
    [(legalcode_uri, None)]
    """
    qstring = """
       PREFIX cc: <http://creativecommons.org/ns#>

       SELECT ?legalcode
       WHERE {
         <%s> cc:legalcode ?legalcode }"""
    legalcodes = ALL_MODEL.query(qstring % license_uri)
    results = set()

    for result in legalcodes:
        legalcode_uri = str(result['legalcode'])

        qstring = """
           PREFIX dcq: <http://purl.org/dc/terms/>

           SELECT ?lang
           WHERE {
             <%s> dcq:language ?lang }"""
        langs = ALL_MODEL.query(qstring % legalcode_uri)

        lang_results = [str(result['lang'])
                        for result in langs]

        if lang_results:
            results.add(
                (legalcode_uri,
                 str(lang_results[0])))
        else:
            results.add(
                (legalcode_uri, None))

    return results

#####################
## Questions stuff ##
#####################

# The below code will change form eventually, but for now here it is.
from lxml import etree
QUESTION_XML_PATH = pkg_resources.resource_filename(
    'cc.licenserdf', 'xml/questions.xml')

questions_root = etree.parse(QUESTION_XML_PATH).getroot()
