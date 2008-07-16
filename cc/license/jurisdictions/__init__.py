
import RDF
import cc.license
from cc.license.lib import rdf_helper

# because of the unfortunate global-shadowing
list_t = list

def list_uris():
    """Returns sequence of all jurisdiction codes possible. Jurisdiction
       codes are strings that yield a Jurisdiction object when passed
       to cc.license.jurisdiction.Jurisdiction"""
    model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)
    cc_jurisdiction_url = RDF.Uri('http://creativecommons.org/ns#Jurisdiction')
    # grab the url strings from the RDF Nodes
    uris = [ rdf_helper.uri2value(j.subject)
             for j in
             list_t(model.find_statements(
                           RDF.Statement(None, None, cc_jurisdiction_url)))
           ]
    return uris # XXX CACHE ME

# is this a useful / desirable function to have?
def list_codes():
    return [ uri2code(uri) for uri in list_uris() ] # XXX CACHE ME

def list():
    return [ cc.license.Jurisdiction(uri) 
             for uri in list_uris() ] # XXX CACHE ME

def by_code(code):
    uri = 'http://creativecommons.org/international/%s/' % code
    return cc.license.Jurisdiction(uri)

def uri2code(uri):
    """Given a jurisdiction URI, parse out the jurisdiction short code."""
    blen = len('http://creativecommons.org/international/')
    return uri[blen:-1]
