import selectors
import formatters
import jurisdictions
from _lib.classes import License, Question
from jurisdictions.classes import Jurisdiction
from selectors.classes import LicenseSelector
from _lib.functions import locales
from _lib.exceptions import CCLicenseError

__all__ = ['selectors', 'formatters', 'jurisdictions', # modules
           'License', 'Question', 'Jurisdiction', 'LicenseSelector', # classes
           'locales', # functions
           'CCLicenseError', # exceptions
          ]

# fail with a useful error message if librdf not installed
try:
    import RDF
except ImportError:
    raise CCLicenseError, "Redland RDF library (librdf) not installed"
