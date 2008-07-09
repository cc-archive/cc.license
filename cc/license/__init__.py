
import RDF # TODO: because of all_jurisdictions; should RDF only be in helper?
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
    return codes # TODO: cache this somewhere?

# XXX Broken, doesn't do what's expected
def jurisdictions(): # TODO: tests!
    """Returns sequence of all jurisdictions possible, 
       as Jurisdiction objects."""
    return [jurisdiction.Jurisdiction(code) for code in jurisdiction_codes()]

def locales(): # TODO: tests!
    """Returns a sequence of all locales possible.
       A locale is a string that represents the language of 
       a jurisdiction.
       
       Note that locales are not the same as jurisdiction codes."""
    pass
