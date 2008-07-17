
import cc.license
from cc.license.lib.rdf_helper import questions_root

def test_constructor():
    q = cc.license.Question(questions_root, 'standard', 'commercial')
    assert q.id == 'commercial'
    q2 = cc.license.Question(questions_root, 'standard', 'derivatives')
    assert q2.id == 'derivatives'

class TestQuestion:
    pass
