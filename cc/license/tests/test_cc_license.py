"""Tests for functionality within the cc.license module.
   This file is a catch-all for tests with no place else to go."""
from builtins import object

import cc.license
import nose.tools

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == str
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales

def test_by_uri():
    uri = 'http://creativecommons.org/licenses/by/3.0/'
    lic = cc.license.selectors.choose('standard').by_uri(uri)
    assert lic == cc.license.by_uri(uri)

def test_by_uri_fails():
    assert cc.license.by_uri('roflcopter') == None

def test_by_code():
    lic = cc.license.selectors.choose('standard').by_code('by')
    assert lic == cc.license.by_code('by')
    lic2 = cc.license.selectors.choose('recombo').by_code('sampling')
    assert lic2 == cc.license.by_code('sampling')

def test_by_code_old_ndnc():
    """
    Old licenses were nd-nc which are now nc-nd.  by_code should
    handle that... make sure it does.
    """
    lic = cc.license.by_code('by-nc-nd', version='1.0')
    assert lic.uri == "http://creativecommons.org/licenses/by-nd-nc/1.0/"

    # Also for selectors
    lic = cc.license.selectors.choose('standard').by_code(
        'by-nc-nd', version='1.0')
    assert lic.uri == "http://creativecommons.org/licenses/by-nd-nc/1.0/"

    # But... obviously don't correct where we shouldn't.
    lic = cc.license.by_code('by-nc-nd', version='3.0')
    assert lic.uri == "http://creativecommons.org/licenses/by-nc-nd/3.0/"
    lic = cc.license.selectors.choose('standard').by_code(
        'by-nc-nd', version='3.0')
    assert lic.uri == "http://creativecommons.org/licenses/by-nc-nd/3.0/"

def test_by_code_jurisdiction():
    lic = cc.license.selectors.choose('standard').by_code('by',
                                                          jurisdiction='jp')
    assert lic == cc.license.by_code('by', jurisdiction='jp')

def test_by_code_version():
    lic = cc.license.selectors.choose('standard').by_code('by',
                                                          version='2.0')
    assert lic == cc.license.by_code('by', version='2.0')
    
def test_by_code_all():
    lic = cc.license.selectors.choose('standard').by_code('by-nc',
                                                          jurisdiction='jp',
                                                          version='2.0')
    assert lic == cc.license.by_code('by-nc', jurisdiction='jp', version='2.0')

def test_by_code_fails():
    lic = cc.license.by_code('lollerskates')
    assert lic == None

class TestPublicApi(object):

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
