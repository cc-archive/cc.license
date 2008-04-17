import nose.tools

def test_list_selectors():
    """Test that we can get a list of selectors."""

    import cc.license
    
    cc.license.list_selectors()

    nose.tools.assert_true(type(cc.license.list_selectors()) == list)


def test_get_selector():
    """get_selector() must return a valid ISelector for each selector."""

    from zope.interface import implementedBy
    import cc.license
    from cc.license import interfaces
    
    for selector_id in cc.license.list_selectors():

        s = cc.license.get_selector(selector_id)
        print selector_id, 'baby'
        nose.tools.assert_true(
            interfaces.ILicenseSelector in implementedBy(s))
    
def test_get_selector_key_error():
    """get_selector() should raise a KeyError if supplied with an invalid
    selector id."""

    import cc.license

    nose.tools.assert_raises(KeyError,
                             cc.license.get_selector, 'roflcopter')
