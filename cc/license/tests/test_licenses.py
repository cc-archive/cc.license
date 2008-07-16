
from zope.interface import implementedBy
import cc.license

class TestAll:

    def __init__(self):
        self.stdsel = cc.license.selectors.choose('standard')
        self.smpsel = cc.license.selectors.choose('recombo')
        self.pdsel = cc.license.selectors.choose('publicdomain')

    def test_license_class(self):
        stdlic = self.stdsel.by_code('by')
        assert self.stdsel.id == stdlic.license_class
        smplic = self.smpsel.by_code('sampling')
        assert self.smpsel.id == smplic.license_class
        pdlic = self.pdsel.by_code('publicdomain')
        assert self.pdsel.id == pdlic.license_class

    def test_version(self):
        uri = 'http://creativecommons.org/licenses/by-sa/1.0/'
        lic = self.stdsel.by_uri(uri)
        assert lic.version == u'1.0'

    # TODO: write test_jurisdiction

    def test_title(self):
        lic = self.stdsel.by_code('by')
        assert lic.title() == lic.title('en')
        assert lic.title('en') == u'Attribution'
        assert lic.title('es') == u'Reconocimiento'
        assert lic.title('de') == u'Namensnennung'

    def test_description(self):
        # has a description
        lic = self.stdsel.by_code('by')
        assert lic.description() == u'You must attribute the\nwork in the manner specified by the author or licensor.'
        assert lic.description('es') == u'El licenciador permite copiar, distribuir y comunicar p\xfablicamente la obra. A cambio, hay que reconocer y citar al autor original.'
        # doesn't have a description
        lic2 = self.stdsel.by_code('by-sa')
        assert lic2.description() == ''

class TestStandard:

    def setUp(self):
        self.selector = cc.license.selectors.choose('standard')

    def test_bysa_same(self):
        lic1 = self.selector.by_code('by-sa')
        lic2 = self.selector.by_code('by-sa')
        assert lic1 == lic2
        assert lic1 is lic2 # For "efficiency", why not?

    def test_bysa_generic(self):
        lic = self.selector.by_code('by-sa')
        assert lic.jurisdiction == '' # generic jurisdiction is empty string
        # assert_true(lic.libre) # FIXME: Should this be here?

    def test_bysa_us(self):
        lic = self.selector.by_code('by-sa', jurisdiction='us', version='1.0')
        assert lic is None

        lic = self.selector.by_code('by-sa', jurisdiction='us', version='3.0')
        assert lic.jurisdiction == 'http://creativecommons.org/international/us/'
        # FIXME: Above should return an IJurisdiction
        # assert_true(lic.libre) # FIXME: Should this be here?

        # Now, test automatic version selection - but FIXME
        # do that later.

class TestSampling:

    def setUp(self):
        self.selector = cc.license.selectors.choose('recombo')

    def test_title(self):
        lic = self.selector.by_code('sampling')
        assert lic.title() == 'Sampling'

class TestPublicDomain:

    def setUp(self):
        self.selector = cc.license.selectors.choose('publicdomain')
        self.lic = self.selector.by_code('publicdomain')

    def test_title(self):
        assert self.lic.title() == 'Public Domain'

    def test_title_default(self):
        assert self.lic.title() == self.lic.title('en')
