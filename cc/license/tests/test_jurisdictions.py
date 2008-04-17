import nose.tools

def test_jurisdiction():
    import cc.license.jurisdiction
    mx = cc.license.jurisdiction.Jurisdiction('mx')
    assert 'creativecommons.org.mx' in mx.local_url 
    assert mx.code == 'mx'
    assert mx.launched
    assert mx.id.endswith('mx/')
