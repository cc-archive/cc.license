from rdflib import URIRef
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
    if 'uri' not in _CACHE:
        _CACHE['uri'] = _list_uris()
    return list_t(_CACHE['uri'])

def _list_uris():
    cc_jurisdiction_url = URIRef('http://creativecommons.org/ns#Jurisdiction')
    # grab the url strings from the RDF Nodes
    uris = [ str(j)
             for j in
             rdf_helper.JURI_MODEL.subjects(None, cc_jurisdiction_url)
           ]
    uris.append('') # default jurisdiction
    return uris

# is this a useful / desirable function to have?
def list_codes():
    if 'code' not in _CACHE:
        _CACHE['code'] = _list_codes()
    return list_t(_CACHE['code'])

def _list_codes():
    return [ uri2code(uri) for uri in list_uris() ]

def list():
    if 'juri' not in _CACHE:
        _CACHE['juri'] = _list()
    return list_t(_CACHE['juri'])

def _list():
    return [ cc.license.Jurisdiction(uri) 
             for uri in list_uris() ]

def by_code(code):
    if code == '':
        return cc.license.Jurisdiction('')
    if code not in list_codes():
        # invalid jurisdiction
        return None
    uri = 'http://creativecommons.org/international/%s/' % code
    return cc.license.Jurisdiction(uri)

def uri2code(uri):
    """Given a jurisdiction URI, parse out the jurisdiction short code."""
    if uri == '':
        return '' # trivial case
    base = 'http://creativecommons.org/international/' 
    if not uri.startswith(base):
        raise cc.license.InvalidURIError("Invalid jurisdiction URI")
    blen = len(base)
    return uri[blen:-1]

def get_licenses_by_code(code):
    if code not in list_codes():
        # 'Invalid jurisdiction'
        return None
    if code == '':
        if 'unported' not in list(_CACHE.keys()):
            _CACHE['unported'] = []
            uris = rdf_helper.get_license_uris(
                'http://creativecommons.org/license/')
            for uri in uris:
                l = cc.license.by_uri(uri)
                if l.jurisdiction.title() == 'Unported':
                    _CACHE['unported'].append(uri)
        return _CACHE['unported']
    uri = 'http://creativecommons.org/international/%s/' % code
    return rdf_helper.get_jurisdiction_licenses(uri)
