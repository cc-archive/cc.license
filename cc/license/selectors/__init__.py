
from cc.license._lib import rdf_helper
from cc.license._lib.exceptions import CCLicenseError
import classes

SELECTORS = {}

for uri, lcode in rdf_helper.get_selector_info():
    SELECTORS[lcode] = classes.LicenseSelector(uri, lcode)

def choose(license_class):
    """Return an instance of ILicenseSelector for a specific license
       class id. The default license class id is 'standard'"""
    if license_class not in SELECTORS.keys():
        raise CCLicenseError, "License class %s does not exist" % license_class

    return SELECTORS[license_class]

def list():
    """Return a list of available selector IDs."""
    return SELECTORS.keys()
