
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
        assert type(s) == unicode

def test_get_selector():
    """selectors.choose() must return a valid ISelector for each selector."""
    for selector_id in cc.license.selectors.list():
        s = cc.license.selectors.choose(selector_id)
        assert ILicenseSelector in implementedBy(s.__class__)
        s2 = cc.license.selectors.choose(selector_id)
        assert s2 is s # singletons, in a way

def test_id_and_uri():
    for sid in cc.license.selectors.list():
        s = cc.license.selectors.choose(sid)
        assert s.id == sid
        assert 'http://creativecommons.org/license' in s.uri
    
def test_get_selector_key_error():
    """selectors.choose() should raise a CCLicenseError if supplied 
       with an invalid selector id."""
    nose.tools.assert_raises(CCLicenseError,
                             cc.license.selectors.choose, 'roflcopter')

def test_questions():
    sel = cc.license.selectors.choose('standard')
    assert type(sel.questions()) == list
    assert len(sel.questions()) != 0
    for q in sel.questions():
        assert type(q) == cc.license.Question

def test_pd_questions():
    sel = cc.license.selectors.choose('publicdomain')
    assert type(sel.questions()) == list
    assert len(sel.questions()) == 0
