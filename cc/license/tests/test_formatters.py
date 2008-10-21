
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

class TestHTMLFormatter:

    def __init__(self):
        self.lic = cc.license.by_code('by')
        self.html = cc.license.formatters.HTML

    # XXX not wrapped in <html> tags
    def _validate(self, output):
        relax_validate(RELAX_HTML, '<html>' + output + '</html>')

    def test_basic(self):
        output = self.html.format(self.lic, locale='en')
        self._validate(output)

    def test_work_format(self):
        for format in ('Audio', 'Video', 'Image', 'Text', 'Interactive'):
            work_dict = {'format':format}
            output = self.html.format(self.lic, work_dict=work_dict)
            self._validate(output)

    def test_invalid_work_format(self):
        work_dict = {'format':'roflcopter'}
        output = self.html.format(self.lic, work_dict=work_dict)
        self._validate(output)


class TestPublicApi:

    def __init__(self):
        self.dir = dir(cc.license.formatters)

    def test_aliased_formatters(self):
        assert 'HTML' in self.dir

    def test_functions(self):
        for f in ('choose', 'list'):
            assert f in self.dir


class TestFilters:

    def __init__(self):
        self.lic = cc.license.by_code('by')
        self.html = cc.license.formatters.HTML
        self.src_str = 'rel="dc:source"'
        self.perm_str = 'rel="cc:morePermissions"'

    def test_permissions_presence(self):
        s = self.html.format(self.lic, {'more_permissions_url':'ASDFASDF'})
        assert self.perm_str in s

    def test_permissions_absence(self):
        s = self.html.format(self.lic)
        assert self.perm_str not in s

    def test_source_presence(self):
        s = self.html.format(self.lic, {'source_work':'ASDFASDF'})
        assert self.src_str in s

    def test_source_absence(self):
        s = self.html.format(self.lic)
        assert self.src_str not in s


class TestCustomization:

    def __init__(self):
        self.formatters = []
        for s in cc.license.formatters.list():
            self.formatters.append(cc.license.formatters.choose(s))

    def test_repr(self):
        for f in self.formatters:
            r = repr(f)
            assert f.id in r
            assert r.startswith('<')
            assert r.endswith('>')

    def test_str(self):
        for f in self.formatters:
            s = str(f)
            assert f.title in s
