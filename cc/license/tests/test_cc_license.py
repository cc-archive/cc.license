"""Tests for functionality within the cc.license module.
   This file is a catch-all for tests with no place else to go."""

import cc.license
import nose.tools

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales

def test_by_uri():
    uri = 'http://creativecommons.org/licenses/by/3.0/'
    lic = cc.license.selectors.choose('standard').by_uri(uri)
    assert lic == cc.license.by_uri(uri)

def test_by_uri_fails():
    nose.tools.assert_raises(cc.license.CCLicenseError,
                             cc.license.by_uri, 'roflcopter')

def test_by_code():
    lic = cc.license.selectors.choose('standard').by_code('by')
    assert lic == cc.license.by_code('by')
    lic2 = cc.license.selectors.choose('recombo').by_code('sampling')
    assert lic2 == cc.license.by_code('sampling')

def test_by_code_fails():
    nose.tools.assert_raises(cc.license.CCLicenseError,
                             cc.license.by_code, 'lollerskates')

class TestPublicApi:

    def __init__(self):
        self.cc_dir = dir(cc.license)

    def test_classes(self):
        for c in ('Jurisdiction', 'License', 'Question', 'LicenseSelector'):
            assert c in self.cc_dir

    def test_modules(self):
        for m in ('selectors', 'formatters', 'jurisdictions'):
            assert m in self.cc_dir

    def test_functions(self):
        for f in ('locales', 'by_code', 'by_uri'):
            assert f in self.cc_dir

    def test_exceptions(self):
        assert 'CCLicenseError' in self.cc_dir
