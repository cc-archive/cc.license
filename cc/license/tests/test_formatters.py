
import nose.tools
from zope.interface import implementedBy
import os

import cc.license
from cc.license import CCLicenseError
from cc.license._lib.interfaces import ILicenseFormatter
from cc.license.tests import relax_validate, RELAX_PATH

RELAX_HTML = os.path.join(RELAX_PATH, 'html_rdfa.relax.xml')

def test_list_formatters():
    """Test that we can get a list of formatter strings."""
    formatters = cc.license.formatters.list()
    assert type(formatters) == list
    for f in formatters:
        assert type(f) == str

def test_get_formatter():
    """formatters.choose() must return a valid IFormatter for each formatter."""
    for formatter_id in cc.license.formatters.list():
        f = cc.license.formatters.choose(formatter_id)
        print formatter_id, 'baby'
        assert ILicenseFormatter in implementedBy(f.__class__)
        f2 = cc.license.formatters.choose(formatter_id)
        assert f2 is f # singletons
    
def test_get_formatter_key_error():
    """formatters.choose() should raise a CCLicenseError if supplied 
       with an invalid formatter id."""
    nose.tools.assert_raises(CCLicenseError,
                             cc.license.formatters.choose, 'roflcopter')

def test_basic_format():
    lic = cc.license.selectors.choose('standard').by_code('by')
    output = cc.license.formatters.HTML.format(lic, locale='en')
    relax_validate(RELAX_HTML, output)

class TestPublicApi:

    def __init__(self):
        self.dir = dir(cc.license.formatters)

    def test_aliased_formatters(self):
        assert 'HTML' in self.dir

    def test_functions(self):
        for f in ('choose', 'list'):
            assert f in self.dir
