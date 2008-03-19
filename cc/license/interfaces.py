from zope.interface import Interface, Attribute

class ILicenseSelector(Interface):
    """License selection for a particular class of license."""

    def by_code(license_code, jurisdiction='-'):
        pass

    def by_uri(uri, absolute=True):
        """Process a URI and return the appropriate ILicense object.
        If unable to produce a License from the URI, return None."""

    def by_answers(in_dict):
        """Issue a license based on a dict of answers; return 
        an ILicense object."""

    jurisdictions = Attribute(u"A sequence of IJurisdiction objects.")
    
    # YYY perhaps unnecessary
    versions = Attribute(u"A sequence of available versions for this class.")

class ILicense(Interface):
    """License metadata for a specific license."""

    license_class = Attribute(u"The license class this license belongs to.")

    name = Attribute(u"The human readable name for this license.")
    version = Attribute(u"The number version for the license.")
    jurisdiction = Attribute(u"The jurisdiction for the license.")
    uri = Attribute(u"The fully qualified URI of the license.")

    current_version
    deprecated
    superseded
    code

    libre = Attribute(u"Returns True if this is a 'Libre' license.")

class IJurisdiction(Interface):
    """Jurisdiction metadata."""

    code = Attribute(u"")
    local_url = Attribute(u"")

    launched = Attribute(u"")
