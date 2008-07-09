
import cc.license
import cc.license.jurisdiction

# TODO: rename and organize more sensically

def test_jurisdiction():
    mx = cc.license.jurisdiction.Jurisdiction('mx')
    assert 'creativecommons.org.mx' in mx.local_url 
    assert mx.code == 'mx'
    assert mx.launched
    assert mx.id.endswith('mx/')

# TODO: additional tests exercising the output
def test_jurisdictions():
    jurisdictions = cc.license.jurisdictions()
    for j in jurisdictions:
        assert type(j) == cc.license.jurisdiction.Jurisdiction

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

def test_locales():
    locales = cc.license.locales()
    for l in locales:
        assert type(l) == unicode
    for c in ('en', 'de', 'he', 'ja', 'fr'):
        assert c in locales
