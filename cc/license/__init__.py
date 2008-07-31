import selectors
import formatters
from lib.classes import License, Question
from jurisdictions.classes import Jurisdiction
from selectors.classes import LicenseSelector
from lib.functions import locales
from lib.exceptions import CCLicenseError

# fail with a useful error message if librdf not installed
try:
    import RDF
except ImportError:
    raise CCLicenseError, "Redland RDF library (librdf) not installed"
