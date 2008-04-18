import nose.tools

def test_find_pd():
    from zope.interface import implementedBy
    import cc.license

    pd_selector = cc.license.get_selector('publicdomain')
    pd = pd_selector.by_code('publicdomain')
    return pd

def test_pd():
    pd = test_find_pd()
    assert pd.libre
    assert pd.jurisdiction == 'Your mom'


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


