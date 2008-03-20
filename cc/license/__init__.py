import selectors
import formatters

SELECTORS = {
    'standard'     : selectors.standard.Selector,
    'recombo'      : selectors.sampling.Selector,
    'publicdomain' : selectors.publicdomain.Selector,
    }


FORMATTERS = {
    'html+rdfa'    : formatters.rdfa.Formatter,
}

def list_selectors():
    """Return a list of available selector IDs."""

    return SELECTORS.keys()

def get_selector(license_class=''):
    """Return the ILicenseSelector for a specific class."""

    return SELECTORS[license_class]

def list_formatters():
    """Return a list of available formatter IDs."""

    return FORMATTERS.keys()

def get_formatter(formatter_id):
    """Return the ILicenseFormatter with the specified id."""

    return FORMATTERS[formatter_id]
