from cc.license.formatters import classes
from cc.license._lib.exceptions import ExistentialException

__all__ = ['HTML', # aliased formatters
           'choose', 'list', # functions
          ]

HTML =  classes.HTMLFormatter()
# aliasing per nathany's "design by wishful thinking"

FORMATTERS = {
    HTML.id : HTML,
    }

PYTHON_BUILTIN_LIST = list

def choose(formatter_id):
    """Return instance of ILicenseFormatter with the specified ID."""
    if formatter_id not in PYTHON_BUILTIN_LIST(FORMATTERS.keys()):
        raise ExistentialException("Formatter %s does not exist" % formatter_id)

    return FORMATTERS[formatter_id]

def list():
    """Return a list of available formatter IDs."""
    return PYTHON_BUILTIN_LIST(FORMATTERS.keys())
