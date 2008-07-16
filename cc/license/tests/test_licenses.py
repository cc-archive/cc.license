
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
        

class TestStandard:

    def setUp(self):
        self.selector = cc.license.selectors.choose('standard')

    def test_bysa_10_up_the_supersede_chain(self):
        lic = self.selector.by_code('by-sa', version='1.0')
        assert lic.superseded # 1.0 we know is old

        highest_lic = lic.current_version
        assert lic.version != highest_lic.version # We know 1.0 is not latest

        highest_by_crawl = lic # to start with
        while highest_by_crawl.superseded:
            started_with = highest_by_crawl
            print 'Started with', started_with.version
            highest_by_crawl = highest_by_crawl.superseded
            print 'Moved on to', highest_by_crawl.version

            # Check that each bump upwards in the chain is the same license
            assert started_with.license_code == highest_by_crawl.license_code

        assert highest_by_crawl.version >= "3.0"

        # Finally, check for equality
        assert highest_by_crawl == highest_lic
        assert highest_by_crawl.current_version == highest_by_crawl

        # FIXME: Later, check that they "is" each other?
        # We don't need that necessarily.

    def test_all_bysa_10_the_same(self):
        lic1 = self.selector.by_code('by-sa')
        lic2 = self.selector.by_code('by-sa')
        assert lic1 == lic2
        assert lic1 is lic2 # For "efficiency", why not?

    def test_bysa_10_has_superseded(self):
        lic = self.selector.by_code('by-sa')
        assert lic.superseded

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

    def test_find_sampling_licenses(self):
        lic = self.selector.by_code('sampling')
        assert not lic.libre 
        assert lic.deprecated 
        lic = self.selector.by_code('sampling+')
        assert not lic.deprecated

class TestPublicDomain:

    def setUp(self):
        self.selector = cc.license.selectors.choose('publicdomain')

    def test_publicdomain(self):
        pd = self.selector.by_code('publicdomain')
        assert pd.libre
        assert pd.jurisdiction == 'Your mom'
        assert not pd.deprecated
        assert pd.jurisdiction == 'Your mom'
        assert pd.license_code == 'publicdomain'
        assert pd.name() == 'Public Domain' == pd.name('en')
        assert pd.name('hr') == u'Javna domena'
