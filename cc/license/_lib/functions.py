from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str

import copy
from distutils.version import StrictVersion
import future.moves.urllib.parse
import rdflib
from . import rdf_helper

from cc.license.jurisdictions.classes import Jurisdiction
from cc.license._lib.exceptions import InvalidURIError
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
            ?x cc:defaultLanguage ?lang .
            ?x rdf:type cc:Jurisdiction .
         }
                  """
    solns = rdf_helper.JURI_MODEL.query(query_string)
    return [str(s['lang']) for s in solns]


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
    if cache_key in _BY_CODE_CACHE:
        return _BY_CODE_CACHE[cache_key]

    for key, selector in list(cc.license.selectors.SELECTORS.items()):
        license = selector.by_code(
            code,
            jurisdiction=jurisdiction,
            version=version)
        if license:
            _BY_CODE_CACHE[cache_key] = license
            return license

    # License for code doesn't exist
    return None

_BY_URI_CACHE = {}

def by_uri(uri):
    """A LicenseSelector-less means of picking a License from a URI."""
    if uri in _BY_URI_CACHE:
        return _BY_URI_CACHE[uri]

    for key, selector in list(cc.license.selectors.SELECTORS.items()):
        if selector.has_license(uri):
            license =  selector.by_uri(uri)
            _BY_URI_CACHE[uri] = license
            return license

    return None

def code_from_uri(uri):
    """Given a URI representing a CC license, parse out the license_code."""
    if uri.startswith(LICENSES_BASE):
        return uri[len(LICENSES_BASE):].split('/')[0]
    elif uri.startswith(CC0_BASE):
        return 'CC0'
    else:
        raise InvalidURIError("Invalid License URI")

def uri2dict(uri):
    """Take a license uri and convert it into a dictionary of values."""
    if uri.startswith(LICENSES_BASE) and uri.endswith('/'):
        base = LICENSES_BASE

        license_info = {}
        raw_info = uri[len(base):]
        raw_info = raw_info.rstrip('/')

        info_list = raw_info.split('/')

        if len(info_list) not in (1,2,3):
            raise InvalidURIError("Invalid Creative Commons URI: <%s>"%uri)

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
        raise InvalidURIError("Invalid Creative Commons URI: <%s>" % uri)

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

        if 'jurisdiction' in license_info:
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

        # Apparently urlparse.urljoin is broken, or handles /'s differently
        # than I expect; if string is empty, concatenating yields a single '/'
        # which brings the URI up a level.
        base = future.moves.urllib.parse.urljoin(base, license_code)
        if not base.endswith('/'):
            base += '/'
        base = future.moves.urllib.parse.urljoin(base, version)
        if not base.endswith('/'):
            base += '/'

        if jurisdiction:
            base = future.moves.urllib.parse.urljoin(base, jurisdiction)
            if not base.endswith('/'):
                base += '/'

        return base


def current_version(code, jurisdiction=None):
    """Given a license code and optional jurisdiction, determine what
       the current (latest) license version is. Returns a just the version
       number, as a string. 'jurisdiction' should be a short code and
       not a jurisdiction URI."""
    versions = all_possible_license_versions(code, jurisdiction)
    current = ''
    if len(versions):
        current = str(versions[-1].version)
    return current


def sort_licenses(x, y):
    """
    Sort function for licenses.
    """
    x_version = StrictVersion(x.version)
    y_version = StrictVersion(y.version)

    if x_version > y_version:
        return 1
    elif x_version == y_version:
        return 0
    else:
        return -1


ALL_POSSIBLE_VERSIONS_CACHE = {}
def all_possible_license_versions(code, jurisdiction=None):
    """
    Given a license code and optional jurisdiction, determine all
    possible license versions available.
    'jurisdiction' should be a short code and not a jurisdiction URI.

    Returns:
     A list of URIs.
    """
    cache_key = (code, jurisdiction)
    if cache_key in ALL_POSSIBLE_VERSIONS_CACHE:
        return ALL_POSSIBLE_VERSIONS_CACHE[cache_key]

    qstring = """
              PREFIX dc: <http://purl.org/dc/elements/1.1/>

              SELECT ?license
              WHERE {
                ?license dc:identifier '%s' }"""
    solns = rdf_helper.ALL_MODEL.query(qstring % str(code))

    license_results = [
        cc.license.by_uri(str(result['license']))
        for result in solns]

    jurisdiction_obj = cc.license.jurisdictions.by_code(str(jurisdiction or ''))

    # only keep results with the same jurisdiction
    license_results = [lic for lic in license_results
                       if lic.jurisdiction == jurisdiction_obj]

    license_results.sort(sort_licenses)
    ALL_POSSIBLE_VERSIONS_CACHE[cache_key] = license_results

    return license_results


def all_possible_answers(list_of_questions):
    """Given a sequence of IQuestions, return a list of answer dictionaries.
       These are meant to be used with LicenseSelector.by_answers. This
       function will generate a set of answer dictionaries that embody
       every possible permutation of the answers to the questions given."""
    questions = copy.deepcopy(list_of_questions)
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
    if license_class in _VALID_JURISDICTIONS_CACHE:
        return _VALID_JURISDICTIONS_CACHE[license_class]

    # TODO: use license_class here
    solns = rdf_helper.ALL_MODEL.query(
        str('PREFIX cc: <http://creativecommons.org/ns#> '
            'SELECT ?jurisdiction WHERE '
            '{ ?license cc:licenseClass <http://creativecommons.org/license/> .'
            '  ?license cc:jurisdiction ?jurisdiction }'))

    jurisdictions = set(
        [str(result['jurisdiction'])
         for result in solns])

    _VALID_JURISDICTIONS_CACHE[license_class] = jurisdictions

    return jurisdictions


_SELECTOR_JURISDICTIONS_CACHE = {}

def get_selector_jurisdictions(selector_name='standard'):
    """
    Get all of the launched jurisdictions that licenses in this
    selector are part of
    """
    if selector_name in _SELECTOR_JURISDICTIONS_CACHE:
        return _SELECTOR_JURISDICTIONS_CACHE[selector_name]

    selector = cc.license.selectors.choose(selector_name)
    qstring = "\n".join(
        ["PREFIX cc: <http://creativecommons.org/ns#>",
         "SELECT ?license",
         "WHERE {?license cc:licenseClass <%s>}" % str(selector.uri)])
    solns = rdf_helper.ALL_MODEL.query(qstring)

    # This is so stupid, but if we add a WHERE clause for
    # jurisdictions in the query string it takes approximately 5
    # million years.
    licenses = [
        cc.license.by_uri(str(result['license']))
        for result in solns]

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
