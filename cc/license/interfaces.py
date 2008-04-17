from zope.interface import Interface, Attribute

class IJurisdiction(Interface):
    """Jurisdiction metadata."""

    code = Attribute(u"The short code for this jurisdiction.")
    id = Attribute(u"String URL of the jurisdiction ID, like "
                   "http://creativecommons.org/international/us")
    local_url = Attribute(u"The URL of the local jurisdiction site, like http://creativecommons.org.mx/.")
    launched = Attribute(u"Boolean attribute; True if this jurisdiction has "
                         "launched")

class ILicense(Interface):
    """License metadata for a specific license."""

    license_class = Attribute(u"The license class this license belongs to.")

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
    def name(language='en'):
        '''Return the human-readable name of this license.  It is a method so
        a language parameter can be passed in.'''


class ILicenseSelector(Interface):
    """License selection for a particular class of license."""

    id = Attribute(u"The unique identifier for this selector.")

    def by_code(license_code, jurisdiction=None, version=None):
        """Return the ILicense object cooresponding to the license code (eg,
        "by-sa") and optional jurisdiction and version.  If
        jurisdiction is None, an Unported license is returned.  If
        version is None, the latest available version is returned.  If
        a license can not be found in this selector, return None."""

    def by_uri(uri):
        """Process a URI and return the appropriate ILicense object.
        If unable to produce a License from the URI, return None."""

    def by_answers(answers_dict):
        """Issue a license based on a dict of answers; return 
        an ILicense object.

        Question and answer information exists in questions.xml;
        there is a jurisdiction "question" which should go away.
        """

    def questions():
        """Return a String(?) containing the XML describing the questions
        for this license class."""

    jurisdictions = Attribute(u"A sequence of IJurisdiction objects.")
    versions = Attribute(u"A sequence of available versions for this class.")


class ILicenseFormatter(Interface):
    """Support for formatting metadata for an issued license for output."""

    id = Attribute(u"The unique identifier for this formatter.")

    def format(license, work_dict={}, locale='en'):
        """Return a string serialization for the license, optionally 
        incorporating the work metadata and locale."""

