import selectors
import formatters

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
    """Return the ILicenseSelector for a specific class."""

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

    return FORMATTERS[formatter_id]
