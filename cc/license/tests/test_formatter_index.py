
import nose.tools
from zope.interface import implementedBy
import cc.license

def test_list_formatters():
    """Test that we can get a list of formatter strings."""
    formatters = cc.license.list_formatters()
    assert type(formatters) == list
    for f in formatters:
        assert type(f) == str

def test_get_formatter():
    """get_formatter() must return a valid IFormatter for each formatter."""
    for formatter_id in cc.license.list_formatters():
        s = cc.license.get_formatter(formatter_id)
        print formatter_id, 'baby'
        assert cc.license.interfaces.ILicenseFormatter in implementedBy(s)
    
def test_get_formatter_key_error():
    """get_formatter() should raise a KeyError if supplied with an invalid
    formatter id."""
    nose.tools.assert_raises(KeyError,
                             cc.license.get_formatter, 'roflcopter')
