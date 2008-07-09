
import RDF # TODO: because of jurisdictions; should RDF only be in helper?
import selectors
import formatters
import rdf_helper
import jurisdiction

SELECTORS = {
    'standard'     : [selectors.standard.Selector, None],
    'recombo'      : [selectors.sampling.Selector, None],
    'publicdomain' : [selectors.publicdomain.Selector, None],
    }


FORMATTERS = {
    'html+rdfa'    : formatters.rdfa.Formatter,
}

def list_selectors():
    """Return a list of available selector IDs."""

    return SELECTORS.keys()

def get_selector(license_class=''):
    """Return an ILicenseSelector instance for a specific class."""

    klass, instance = SELECTORS[license_class]
    if not instance: # then instantiate it
        SELECTORS[license_class][1] = klass()
    # No matter what, return the instance in the dictionary
    return SELECTORS[license_class][1]

def list_formatters():
    """Return a list of available formatter IDs."""

    return FORMATTERS.keys()

def get_formatter(formatter_id):
    """Return the ILicenseFormatter with the specified id."""

    # XXX cache me
    return FORMATTERS[formatter_id]


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
    return [jurisdiction.Jurisdiction(code) for code in jurisdiction_codes()]

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
