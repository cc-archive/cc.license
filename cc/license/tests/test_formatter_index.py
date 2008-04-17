import nose.tools

def test_list_formatters():
    """Test that we can get a list of formatters."""

    import cc.license
    
    cc.license.list_formatters()

    nose.tools.assert_true(type(cc.license.list_formatters()) == list)


def test_get_formatter():
    """get_formatter() must return a valid IFormatter for each formatter."""

    from zope.interface import implementedBy
    import cc.license
    from cc.license import interfaces
    
    for formatter_id in cc.license.list_formatters():

        s = cc.license.get_formatter(formatter_id)
        print formatter_id, 'baby'
        nose.tools.assert_true(
            interfaces.ILicenseFormatter in implementedBy(s))
    
def test_get_formatter_key_error():
    """get_formatter() should raise a KeyError if supplied with an invalid
    formatter id."""

    import cc.license

    nose.tools.assert_raises(KeyError,
                             cc.license.get_formatter, 'roflcopter')
