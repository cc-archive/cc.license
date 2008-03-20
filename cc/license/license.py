from zope.interface import implements

import interfaces

class License(object):
    """Base class for ILicense implementation modeling a specific license."""
    implements(interfaces.ILicense)


    """
    license_class = Attribute(u"The license class this license belongs to.")

    name = Attribute(u"The human readable name for this license.")
    version = Attribute(u"The number version for the license.")
    jurisdiction = Attribute(u"The jurisdiction for the license.")
    uri = Attribute(u"The fully qualified URI of the license.")

    current_version = Attribute(u"The ILicense of the current version of "
                                "this jurisdiction + license.")
    deprecated = Attribute(u"Boolean attribute; True if this license is "
                           "deprecated")
    superseded = Attribute(u"Boolean attribute; True if this license has "
                           "been replaced with a newer version.")
    license_code = Attribute(u"The short alpha code for this license.")
    libre = Attribute(u"Returns True if this is a 'Libre' license.")

    """
