
import cc.license.jurisdiction

def test_jurisdiction():
    mx = cc.license.jurisdiction.Jurisdiction('mx')
    assert 'creativecommons.org.mx' in mx.local_url 
    assert mx.code == 'mx'
    assert mx.launched
    assert mx.id.endswith('mx/')
