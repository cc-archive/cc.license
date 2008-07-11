"""Tests for functionality within the cc.license module.
   This file is a catch-all for tests with no place else to go."""

import cc.license

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales
