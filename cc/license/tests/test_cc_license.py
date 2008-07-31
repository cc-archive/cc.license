"""Tests for functionality within the cc.license module.
   This file is a catch-all for tests with no place else to go."""

import cc.license

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales

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
        assert 'locales' in self.cc_dir

    def test_exceptions(self):
        assert 'CCLicenseError' in self.cc_dir
