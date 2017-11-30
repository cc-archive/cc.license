from __future__ import absolute_import
from . import selectors
from . import formatters
from . import jurisdictions
from ._lib.classes import License, Question, JurisdictionQuestion
from .jurisdictions.classes import Jurisdiction
from .selectors.classes import LicenseSelector
from ._lib.functions import locales, by_code, by_uri
from ._lib.exceptions import CCLicenseError, InvalidURIError
from ._lib.exceptions import SelectorQAError, ExistentialException

__all__ = ['selectors', 'formatters', 'jurisdictions', # modules
           'License', 'Question', 'Jurisdiction', 'LicenseSelector', # classes
           'locales', 'by_code', 'by_uri', # functions
           'CCLicenseError', 'InvalidURIError', # exceptions
           'SelectorQAError', 'ExistentialException'
          ]

# fail with a useful error message if librdf not installed
try:
    import RDF
    del RDF # we really don't need it imported
except ImportError:
    raise CCLicenseError("Redland RDF library (librdf) not installed")


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

