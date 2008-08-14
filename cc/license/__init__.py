import selectors
import formatters
import jurisdictions
from _lib.classes import License, Question
from jurisdictions.classes import Jurisdiction
from selectors.classes import LicenseSelector
from _lib.functions import locales, by_code, by_uri
from _lib.exceptions import CCLicenseError

__all__ = ['selectors', 'formatters', 'jurisdictions', # modules
           'License', 'Question', 'Jurisdiction', 'LicenseSelector', # classes
           'locales', 'by_code', 'by_uri', # functions
           'CCLicenseError', # exceptions
          ]

# fail with a useful error message if librdf not installed
try:
    import RDF
    del RDF # we really don't need it imported
except ImportError:
    raise CCLicenseError, "Redland RDF library (librdf) not installed"


########################
## Cleanup for librdf ##
########################

import atexit

def _rdf_cleanup():
    del _lib.rdf_helper.ALL_MODEL
    del _lib.rdf_helper.JURI_MODEL
    del _lib.rdf_helper.SEL_MODEL
    del selectors.SELECTORS

atexit.register(_rdf_cleanup)

