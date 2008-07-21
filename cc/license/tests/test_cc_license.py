"""Tests for functionality within the cc.license module.
   This file is a catch-all for tests with no place else to go."""

import cc.license

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales

def test_cc_license_classes():
    cc_dir = dir(cc.license)
    assert 'Jurisdiction' in cc_dir
    assert 'License' in cc_dir
    assert 'Question' in cc_dir
    assert 'LicenseSelector' in cc_dir
