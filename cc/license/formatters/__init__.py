
import classes
from cc.license._lib.exceptions import CCLicenseError

__all__ = ['HTML', # aliased formatters
           'choose', 'list', # functions
          ]

HTML =  classes.HTMLFormatter() 
# aliasing per nathany's "design by wishful thinking"

FORMATTERS = {
    HTML.id : HTML,
    }

def choose(formatter_id):
    """Return instance of ILicenseFormatter with the specified ID."""
    if formatter_id not in FORMATTERS.keys():
        raise CCLicenseError, "Formatter %s does not exist" % formatter_id

    return FORMATTERS[formatter_id]

def list():
    """Return a list of available formatter IDs."""
    return FORMATTERS.keys()
