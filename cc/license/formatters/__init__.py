import rdfa

FORMATTERS = {
    'html+rdfa' : [rdfa.Formatter, None],
    }

def choose(formatter_id):
    """Return instance of ILicenseFormatter with the specified ID."""
    fclass, instance = FORMATTERS[formatter_id]

    if instance is None:
        FORMATTERS[formatter_id][1] = fclass()
    # return the instance no matter what
    return FORMATTERS[formatter_id][1]

def list():
    """Return a list of available formatter IDs."""
    return FORMATTERS.keys()
