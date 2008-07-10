
import cc.license
from cc.license.lib.exceptions import CCLicenseError
import nose.tools

# TODO: rename and organize more sensically

def test_jurisdiction():
    mx = cc.license.Jurisdiction('mx')
    assert 'creativecommons.org.mx' in mx.local_url 
    assert mx.code == 'mx'
    assert mx.launched
    assert mx.id.endswith('mx/')

# TODO: additional tests exercising the output
def test_jurisdictions():
    jurisdictions = cc.license.jurisdictions()
    for j in jurisdictions:
        assert type(j) == cc.license.Jurisdiction

def test_jurisdiction_codes():
    codes = cc.license.jurisdiction_codes()
    # scotland is in there, and it's the only one that isn't 2 letters
    assert 'scotland' in codes
    codes.remove('scotland')
    # they are all strings of length 2
    for c in codes:
        assert type(c) == str
        assert len(c) == 2
    # test a few big jurisdictions
    for k in ('us', 'uk', 'fr', 'de', 'jp', 'ca'):
        print k 
        assert k in codes

# XXX this test belongs elsewhere
def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales

def test_titles():
    mx = cc.license.Jurisdiction('mx')
    for t in ('fr', 'ja', 'de', 'en'):
        title = mx.title(t)
        assert type(title) == unicode
        assert len(title) != 0

def test_title_fails():
    mx = cc.license.Jurisdiction('mx')
    nose.tools.assert_raises(CCLicenseError,
                             mx.title, 'roflcopter')

def test_title_default():
    mx = cc.license.Jurisdiction('mx')
    assert mx.title() == mx.title('en')
