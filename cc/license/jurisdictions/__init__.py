
import RDF
import cc.license
from cc.license._lib import rdf_helper

# because of the unfortunate global-shadowing
list_t = list

__all__ = ['list_uris', 'list_codes', 'list',
           'by_code', 'uri2code', # functions
          ]

# caches
_CACHE = {}

def list_uris():
    """Returns sequence of all jurisdiction codes possible. Jurisdiction
       codes are strings that yield a Jurisdiction object when passed
       to cc.license.jurisdiction.Jurisdiction"""
    if not _CACHE.has_key('uri'):
        _CACHE['uri'] = _list_uris()
    return list_t(_CACHE['uri'])

def _list_uris():
    cc_jurisdiction_url = RDF.Uri('http://creativecommons.org/ns#Jurisdiction')
    # grab the url strings from the RDF Nodes
    uris = [ rdf_helper.uri2value(j.subject)
             for j in
             list_t(rdf_helper.JURI_MODEL.find_statements(
                           RDF.Statement(None, None, cc_jurisdiction_url)))
           ]
    uris.append('') # default jurisdiction
    return uris

# is this a useful / desirable function to have?
def list_codes():
    if not _CACHE.has_key('code'):
        _CACHE['code'] = _list_codes()
    return list_t(_CACHE['code'])

def _list_codes():
    return [ uri2code(uri) for uri in list_uris() ]

def list():
    if not _CACHE.has_key('juri'):
        _CACHE['juri'] = _list()
    return list_t(_CACHE['juri'])

def _list():
    return [ cc.license.Jurisdiction(uri) 
             for uri in list_uris() ]

def by_code(code):
    if code == '':
        return cc.license.Jurisdiction('')
    if code not in list_codes():
        raise cc.license.CCLicenseError, 'Invalid jurisdiction'
    uri = 'http://creativecommons.org/international/%s/' % code
    return cc.license.Jurisdiction(uri)

def uri2code(uri):
    """Given a jurisdiction URI, parse out the jurisdiction short code."""
    if uri == '':
        return '' # trivial case
    base = 'http://creativecommons.org/international/' 
    if not uri.startswith(base):
        raise cc.license.CCLicenseError, "Malformed jurisdiction URI"
    blen = len(base)
    return uri[blen:-1]

def get_licenses_by_code(code):
    if code not in list_codes():
        raise cc.license.CCLicenseError, 'Invalid jurisdiction'
    if code == '':
        if 'unported' not in _CACHE.keys():
            _CACHE['unported'] = []
            uris = rdf_helper.get_license_uris(rdf_helper.ALL_MODEL,
                                               'http://creativecommons.org/license/')
            for uri in uris:
                l = cc.license.by_uri(uri)
                if l.jurisdiction.title() == 'Unported':
                    _CACHE['unported'].append(uri)
        return _CACHE['unported']
    uri = 'http://creativecommons.org/international/%s/' % code
    return rdf_helper.get_jurisdiction_licenses(rdf_helper.ALL_MODEL, uri)
