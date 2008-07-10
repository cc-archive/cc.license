import rdfa

from cc.license.lib.exceptions import CCLicenseError

FORMATTERS = {
    'html+rdfa' : [rdfa.Formatter, None],
    }

def choose(formatter_id):
    """Return instance of ILicenseFormatter with the specified ID."""
    try:
        fclass, instance = FORMATTERS[formatter_id]
    except KeyError:
        raise CCLicenseError, "Formatter %s does not exist" % formatter_id

    if instance is None:
        FORMATTERS[formatter_id][1] = fclass()
    # return the instance no matter what
    return FORMATTERS[formatter_id][1]

def list():
    """Return a list of available formatter IDs."""
    return FORMATTERS.keys()
