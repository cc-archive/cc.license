
import nose.tools
from zope.interface import implementedBy

import cc.license
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib.exceptions import CCLicenseError

def test_list_selectors():
    """Test that we can get a list of selector strings."""
    selectors = cc.license.selectors.list()
    assert type(selectors) == list
    for s in selectors:
        assert type(s) == str

def test_get_selector():
    """selectors.choose() must return a valid ISelector for each selector."""
    for selector_id in cc.license.selectors.list():
        s = cc.license.selectors.choose(selector_id)
        print selector_id, 'baby'
        assert ILicenseSelector in implementedBy(s.__class__)
        s2 = cc.license.selectors.choose(selector_id)
        assert s2 is s # singletons, in a way
    
def test_get_selector_key_error():
    """selectors.choose() should raise a CCLicenseError if supplied 
       with an invalid selector id."""
    nose.tools.assert_raises(CCLicenseError,
                             cc.license.selectors.choose, 'roflcopter')
