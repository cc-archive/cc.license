
import nose.tools
from zope.interface import implementedBy
import cc.license
from cc.license.lib.interfaces import ILicenseSelector

def test_list_selectors():
    """Test that we can get a list of selector strings."""
    selectors = cc.license.list_selectors()
    assert type(selectors) == list
    for s in selectors:
        assert type(s) == str

def test_get_selector():
    """get_selector() must return a valid ISelector for each selector."""
    for selector_id in cc.license.list_selectors():
        s = cc.license.get_selector(selector_id)
        print selector_id, 'baby'
        assert ILicenseSelector in implementedBy(s.__class__)
        s2 = cc.license.get_selector(selector_id)
        assert s2 is s # singletons, in a way
    
def test_get_selector_key_error():
    """get_selector() should raise a KeyError if supplied with an invalid
    selector id."""
    nose.tools.assert_raises(KeyError,
                             cc.license.get_selector, 'roflcopter')
