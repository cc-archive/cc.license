import standard
import sampling
import publicdomain

from cc.license.lib.exceptions import CCLicenseError

# TODO: build list from selectors.rdf
SELECTORS = { # class goes in the 1st spot, singleton in the 2nd
    'standard'     : [standard.Selector, None],
    'recombo'      : [sampling.Selector, None],
    'publicdomain' : [publicdomain.Selector, None],
    }


# XXX maybe raise a different exception if invalid license_class given
def choose(license_class='standard'):
    """Return an instance of ILicenseSelector for a specific license
       class id. The default license class id is 'standard'"""
    try:
        lclass, instance = SELECTORS[license_class]
    except KeyError:
        raise CCLicenseError, "License class %s does not exist" % license_class

    if instance is None:
        SELECTORS[license_class][1] = lclass()
    # return the instance no matter what
    return SELECTORS[license_class][1]

def list():
    """Return a list of available selector IDs."""
    return SELECTORS.keys()
