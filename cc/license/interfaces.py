from zope.interface import Interface, Attribute

class IJurisdiction(Interface):
    """Jurisdiction metadata."""

    code = Attribute(u"The short code for this jurisdiction.")
    local_url = Attribute(u"The URL of the local jurisdiction site.")

    launched = Attribute(u"Boolean attribute; True if this jurisdiction has "
                         "launched")


class ILicense(Interface):
    """License metadata for a specific license."""

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


class ILicenseSelector(Interface):
    """License selection for a particular class of license."""

    id = Attribute(u"The unique identifier for this selector.")

    def by_code(license_code, jurisdiction=None):
        """Return the ILicense object cooresponding to the license code and
        optional jurisdiction.  If jurisdiction is None, an Unported 
        license is returned.  If a licese can not be found in this selector,
        return None."""

    def by_uri(uri, absolute=True):
        """Process a URI and return the appropriate ILicense object.
        If unable to produce a License from the URI, return None."""

    def by_answers(answers_dict):
        """Issue a license based on a dict of answers; return 
        an ILicense object."""

    def questions():
        """Return a String(?) containing the XML describing the questions
        for this license class."""

    jurisdictions = Attribute(u"A sequence of IJurisdiction objects.")
    versions = Attribute(u"A sequence of available versions for this class.")


class ILicenseFormatter(Interface):
    """Support for formatting license metadata for output."""

    id = Attribute(u"The unique identifier for this formatter.")

    def format(license, work_dict={}, locale='en'):
        """Return a string serialization for the license, optionally 
        incorporating the work metadata and locale."""
