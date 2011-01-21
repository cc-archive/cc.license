
from distutils.version import StrictVersion
import urlparse
import RDF
import rdf_helper

from cc.license.jurisdictions.classes import Jurisdiction
from cc.license._lib.exceptions import CCLicenseError
import cc.license


LICENSES_BASE = 'http://creativecommons.org/licenses/'
CC0_BASE = 'http://creativecommons.org/publicdomain/zero/'
PUBLICDOMAIN_MARK_BASE = 'http://creativecommons.org/publicdomain/mark/'


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
    solns = list(query.execute(rdf_helper.JURI_MODEL))
    return [ s['lang'].literal_value['string'] for s in solns ]


_BY_CODE_CACHE = {}

def by_code(code, jurisdiction=None, version=None):
    """A LicenseSelector-less means of picking a License from a code."""

    # rdflib needs string objects, can't handle unicode :|
    code = str(code)
    if jurisdiction:
        jurisdiction = str(jurisdiction)
    if version:
        version = str(version)

    cache_key = (code, jurisdiction, version)
    if _BY_CODE_CACHE.has_key(cache_key):
        return _BY_CODE_CACHE[cache_key]

    for key, selector in cc.license.selectors.SELECTORS.items():
        try:
            license = selector.by_code(
                code,
                jurisdiction=jurisdiction,
                version=version)
            _BY_CODE_CACHE[cache_key] = license
            return license
        except cc.license.CCLicenseError:
            pass

    raise cc.license.CCLicenseError, "License for code doesn't exist"

_BY_URI_CACHE = {}

def by_uri(uri):
    """A LicenseSelector-less means of picking a License from a URI."""
    if _BY_URI_CACHE.has_key(uri):
        return _BY_URI_CACHE[uri]

    for key, selector in cc.license.selectors.SELECTORS.items():
        if selector.has_license(uri):
            license =  selector.by_uri(uri)
            _BY_URI_CACHE[uri] = license
            return license

    raise CCLicenseError, "License for URI doesn't exist"

def code_from_uri(uri):
    """Given a URI representing a CC license, parse out the license_code."""
    if uri.startswith(LICENSES_BASE):
        return uri[len(LICENSES_BASE):].split('/')[0]
    elif uri.startswith(CC0_BASE):
        return 'CC0'
    else:
        raise CCLicenseError, "Invalid License URI"

def uri2dict(uri):
    """Take a license uri and convert it into a dictionary of values."""
    if uri.startswith(LICENSES_BASE) and uri.endswith('/'):
        base = LICENSES_BASE

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

    elif uri.startswith(CC0_BASE) and uri.endswith('/'):
        base = CC0_BASE

        retval = {'code': 'CC0', 'jurisdiction': None}
        retval['version'] = uri.rstrip('/').split('/')[-1]
        return retval

    elif uri.startswith(PUBLICDOMAIN_MARK_BASE) and uri.endswith('/'):
        base = PUBLICDOMAIN_MARK_BASE

        retval = {'code': 'mark', 'jurisdiction': None}
        retval['version'] = uri.rstrip('/').split('/')[-1]
        return retval


    else:
        raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri

def dict2uri(license_info):
    """Take a dictionary of license values and convert it into a uri."""
    if license_info['code'] in ('CC0', 'mark'):
        license_code = license_info['code']
        if license_info.get('version'):
            version = license_info['version']
        else:
            version = current_version(
                license_code, license_info.get('jurisdiction'))
            
        if license_code == 'CC0':
            return CC0_BASE + version + '/'
        elif license_code == 'mark':
            return PUBLICDOMAIN_MARK_BASE + version + '/'
    else:
        base = LICENSES_BASE

        license_code = license_info['code'] # code should always exist

        if license_code == 'publicdomain': # one URI for publicdomain
            return base + 'publicdomain/'

        if license_info.has_key('jurisdiction'):
            jurisdiction = license_info['jurisdiction']
        else:
            jurisdiction = None

        if jurisdiction == '':
            jurisdiction = None

        version = None
        if license_info.get('version'):
            version = license_info['version']

        if not version:
            version = current_version(license_code, jurisdiction)

        # apparently urlparse.urljoin is retarded, or handles /'s differently
        # than i expect; if string is empty, concatenating yields a single '/'
        # which brings the URI up a level.
        base = urlparse.urljoin(base, license_code)
        if not base.endswith('/'):
            base += '/'
        base = urlparse.urljoin(base, version)
        if not base.endswith('/'):
            base += '/'

        if jurisdiction:
            base = urlparse.urljoin(base, jurisdiction)
            if not base.endswith('/'):
                base += '/'

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
    solns = list(query.execute(rdf_helper.ALL_MODEL))
    license_uris = [ str(s['license'].uri) for s in solns ] # XXX CACHE ME
    license_dicts = [ uri2dict(uri) for uri in license_uris ]
    # filter on code
    filtered_dicts = [ d for d in license_dicts if d['code'] == code ]
    # filter on jurisdiction
    if jurisdiction == '' : jurisdiction = None
    if jurisdiction is None:
        filtered_dicts = [ d for d in filtered_dicts
                           if not d.get('jurisdiction') ]
    else:
        filtered_dicts = [ d for d in filtered_dicts
                           if d.has_key('jurisdiction') and
                              d['jurisdiction'] == jurisdiction ]
    if len(filtered_dicts) == 0:
        return '' # didn't find any matching that code and jurisdiction
    # more error checking; found error in publicdomain
    for d in filtered_dicts:
        try:
            d['version']
        except KeyError:
            return ''
    versions = [ StrictVersion(d['version']) for d in filtered_dicts ]
    return str(max(versions))


ALL_POSSIBLE_VERSIONS_CACHE = {}
def all_possible_license_versions(code, jurisdiction=None):
    """
    Given a license code and optional jurisdiction, determine all
    possible license versions available.

    Returns:
     A list of URIs.
    """
    cache_key = (code, jurisdiction)
    if ALL_POSSIBLE_VERSIONS_CACHE.has_key(cache_key):
        return ALL_POSSIBLE_VERSIONS_CACHE[cache_key]

    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?license
              WHERE {
                ?license dc:identifier '%s' }"""
    query = RDF.Query(
        qstring % code,
        query_language='sparql')

    license_results = [
        cc.license.by_uri(str(result['license'].uri))
        for result in query.execute(rdf_helper.ALL_MODEL)]

    # only keep results with the same jurisdiction
    license_results = filter(
        lambda lic: lic.jurisdiction == jurisdiction, license_results)

    license_results.sort(_sort_licenses)
    
    ALL_POSSIBLE_VERSIONS_CACHE[cache_key] = license_results

    return license_results


def all_possible_answers(list_of_questions):
    """Given a sequence of IQuestions, return a list of answer dictionaries.
       These are meant to be used with LicenseSelector.by_answers. This
       function will generate a set of answer dictionaries that embody
       every possible permutation of the answers to the questions given."""
    questions = list(list_of_questions) # copy
    answer_dict_list = []
    answer_dict_list.append({}) # seed

    def recursive_build_answers(adl, qs):
        if len(qs) == 0:
            return adl
        q = qs.pop()
        new_adl = []
        for adict in adl:
            for enum in q.answers():
                answer = enum[1] # the answer value 
                aclone = adict.copy()
                aclone[q.id] = answer
                new_adl.append(aclone)
        return recursive_build_answers(new_adl, qs)

    return recursive_build_answers(answer_dict_list, questions)


_VALID_JURISDICTIONS_CACHE = {}

def get_valid_jurisdictions(license_class='standard'):
    if _VALID_JURISDICTIONS_CACHE.has_key(license_class):
        return _VALID_JURISDICTIONS_CACHE[license_class]
    
    # TODO: use license_class here
    query = RDF.Query(
        str('PREFIX cc: <http://creativecommons.org/ns#> '
            'SELECT ?jurisdiction WHERE '
            '{ ?license cc:licenseClass <http://creativecommons.org/license/> .'
            '  ?license cc:jurisdiction ?jurisdiction }'),
        query_language="sparql")

    jurisdictions = set(
        [unicode(result['jurisdiction'].uri)
         for result in query.execute(rdf_helper.ALL_MODEL)])

    _VALID_JURISDICTIONS_CACHE[license_class] = jurisdictions

    return jurisdictions


_SELECTOR_JURISDICTIONS_CACHE = {}

def get_selector_jurisdictions(selector_name='standard'):
    """
    Get all of the launched jurisdictions that licenses in this
    selector are part of
    """
    if _SELECTOR_JURISDICTIONS_CACHE.has_key(selector_name):
        return _SELECTOR_JURISDICTIONS_CACHE[selector_name]

    selector = cc.license.selectors.choose(selector_name)
    qstring = "\n".join(
        ["SELECT ?license",
         "WHERE (?license cc:licenseClass <%s>)" % str(selector.uri),
         "USING cc FOR <http://creativecommons.org/ns#>"])
    query = RDF.Query(qstring, query_language="rdql")

    # This is so stupid, but if we add a WHERE clause for
    # jurisdictions in the query string it takes approximately 5
    # million years.
    licenses = [
        cc.license.by_uri(str(result['license'].uri))
        for result in query.execute(rdf_helper.ALL_MODEL)]

    # We need to make sure jurisdictions are unique.  The easiest way
    # to do that is have a second set that keeps track of all the
    # codes added so far.
    code_check = set()
    jurisdictions = set()

    for license in licenses:
        jurisdiction = license.jurisdiction
        if jurisdiction.launched and not jurisdiction.code in code_check:
            jurisdictions.add(jurisdiction)
            code_check.add(jurisdiction.code)

    _SELECTOR_JURISDICTIONS_CACHE[selector_name] = jurisdictions

    return jurisdictions
