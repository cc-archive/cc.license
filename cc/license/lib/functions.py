
from distutils.version import StrictVersion
import urlparse
import RDF
import rdf_helper
from classes import Jurisdiction

from cc.license.lib.exceptions import CCLicenseError


def jurisdiction_codes():
    """Returns sequence of all jurisdiction codes possible. Jurisdiction
       codes are strings that yield a Jurisdiction object when passed
       to cc.license.jurisdiction.Jurisdiction"""
    model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)
    cc_jurisdiction_url = RDF.Uri('http://creativecommons.org/ns#Jurisdiction')
    # grab the url strings from the RDF Nodes
    urls = [ rdf_helper.uri2value(j.subject) 
             for j in 
             list(model.find_statements(
                           RDF.Statement(None, None, cc_jurisdiction_url)))
           ]
    # strip the jurisdiction code from the url
    blen = len('http://creativecommons.org/international/')
    codes = [ url[blen:-1] for url in urls ]
    return codes # XXX: cache this somewhere?

def jurisdictions():
    """Returns sequence of all jurisdictions possible, 
       as Jurisdiction objects."""
    return [Jurisdiction(code) for code in jurisdiction_codes()]

def locales():
    """Returns a sequence of all locales possible.
       A locale is a string that represents the language of a jurisdiction.
       Note that locales are not the same as jurisdiction codes."""
    query_string = """
        PREFIX cc: <http://creativecommons.org/ns#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>

        SELECT ?lang
        WHERE
         {
            ?x dc:language ?lang .
            ?x rdf:type cc:Jurisdiction .
         }
                  """
    query = RDF.Query(query_string, query_language='sparql')
    model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)
        # XXX maybe this model should be cached somewhere?
    solns = list(query.execute(model))
    return [ s['lang'].literal_value['string'] for s in solns ]

def code_from_uri(uri):
    """Given a URI representing a CC license, parse out the license_code."""
    base = 'http://creativecommons.org/licenses/'
    return uri.lstrip(base).split('/')[0]

def uri2dict(uri):
    """Take a license uri and convert it into a dictionary of values."""
    base = 'http://creativecommons.org/licenses/'

    # minor error checking
    if not uri.startswith(base) or not uri.endswith('/'):
        raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri

    license_info = {}
    raw_info = uri[len(base):]
    raw_info = raw_info.rstrip('/')

    info_list = raw_info.split('/') 

    if len(info_list) not in (1,2,3):
        raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri

    retval = dict( code=info_list[0] )
    if len(info_list) > 1:
        retval['version'] = info_list[1]
    if len(info_list) > 2:
        retval['jurisdiction'] = info_list[2]

    # XXX perform any validation on the dict produced?
    return retval

def dict2uri(license_info):
    """Take a dictionary of license values and convert it into a uri."""
    base = 'http://creativecommons.org/licenses/'

    license_code = license_info['code'] # code should always exist

    if license_info.has_key('jurisdiction'):
        jurisdiction = license_info['jurisdiction']
    else:
        jurisdiction = None

    version = None
    try:
        version = license_info['version']
    except KeyError:
        pass # Don't get pissed at me Asheesh, I know what I'm doing.
    if not version:
        version = current_version(license_code, jurisdiction)

    base = urlparse.urljoin(base, license_code + '/')
    base = urlparse.urljoin(base, version + '/')

    if jurisdiction:
        base = urlparse.urljoin(base, jurisdiction + '/')

    return base

def current_version(code, jurisdiction=None):
    """Given a license code and optional jurisdiction, determine what
       the current (latest) license version is. Returns a just the version
       number, as a string. 'jurisdiction' should be a short code and
       not a jurisdiction URI."""
    query_string = """
        PREFIX cc: <http://creativecommons.org/ns#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?license
        WHERE
         {
            ?license rdf:type cc:License .
         }
                  """
    query = RDF.Query(query_string, query_language='sparql')
    solns = list(query.execute(rdf_helper.EVERYTHING))
    license_uris = [ str(s['license'].uri) for s in solns ] # XXX CACHE ME
    license_dicts = [ uri2dict(uri) for uri in license_uris ]
    # filter on code
    filtered_dicts = [ d for d in license_dicts if d['code'] == code ]
    # filter on jurisdiction
    if jurisdiction is None:
        filtered_dicts = [ d for d in filtered_dicts
                           if not d.has_key('jurisdiction') ]
    else:
        filtered_dicts = [ d for d in filtered_dicts
                           if d.has_key('jurisdiction') and
                              d['jurisdiction'] == jurisdiction ]
    if len(filtered_dicts) == 0:
        return None # didn't find any matching that code and jurisdiction
    versions = [ StrictVersion(d['version']) for d in filtered_dicts ]
    return str(max(versions))
