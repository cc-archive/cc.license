
import nose.tools
import cc.license
from cc.license.lib.rdf_helper import questions_root
from cc.license.lib.exceptions import CCLicenseError

def test_constructor():
    q = cc.license.Question(questions_root, 'standard', 'commercial')
    assert q.id == 'commercial'
    q2 = cc.license.Question(questions_root, 'standard', 'derivatives')
    assert q2.id == 'derivatives'

def test_constructor_fails():
    nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             questions_root, 'lolcats', 'commercial')
    nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             questions_root, 'standard', 'qwertyitis')
    nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             questions_root, 'azerbaijan', 'icanhascheezburger')
    

class TestQuestion:
    pass
