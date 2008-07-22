
import nose.tools
from zope.interface import implementedBy

import cc.license
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib.exceptions import CCLicenseError

def test_list_selectors():
    """Test that we can get a list of selector strings."""
    selectors = cc.license.selectors.list()
    assert type(selectors) == list
    for s in selectors:
        assert type(s) == unicode

def test_get_selector():
    """selectors.choose() must return a valid ISelector for each selector."""
    for selector_id in cc.license.selectors.list():
        s = cc.license.selectors.choose(selector_id)
        assert ILicenseSelector in implementedBy(s.__class__)
        s2 = cc.license.selectors.choose(selector_id)
        assert s2 is s # singletons, in a way

def test_id_and_uri():
    for sid in cc.license.selectors.list():
        s = cc.license.selectors.choose(sid)
        assert s.id == sid
        assert 'http://creativecommons.org/license' in s.uri
    
def test_get_selector_key_error():
    """selectors.choose() should raise a CCLicenseError if supplied 
       with an invalid selector id."""
    nose.tools.assert_raises(CCLicenseError,
                             cc.license.selectors.choose, 'roflcopter')

class TestQuestions:

    def __init__(self):
        self.std = cc.license.selectors.choose('standard')
        self.pd = cc.license.selectors.choose('publicdomain')

    def test_standard_questions(self):
        questions = self.std.questions()
        assert type(questions) == list
        assert len(questions) != 0
        for q in questions:
            assert type(q) == cc.license.Question

    def test_publicdomain_questions(self):
        questions = self.pd.questions()
        assert type(questions) == list
        assert len(questions) == 0

class TestAnswersStandard:

    def __init__(self):
        self.sel = cc.license.selectors.choose('standard')

    # XXX no test yet
    #def test_use_case(self):
    #    questions = self.sel.questions()
    #    answers = {}

    # XXX no test yet
    #def test_by(self):
    #    answers = {'commercial':'y', 'derivatives':'y'}

    def test_not_implemented(self):
        nose.tools.assert_raises(NotImplementedError, self.sel.by_answers, {})

class TestAnswersSampling:

    def __init__(self):
        self.sel = cc.license.selectors.choose('recombo')


class TestAnswersPublicdomain:

    def __init__(self):
        self.sel = cc.license.selectors.choose('publicdomain')

    def test_no_answers(self):
        lic = self.sel.by_answers({})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Public Domain'
        lic2 = self.sel.by_code('publicdomain')
        assert lic == lic2

    def test_extra_answers(self):
        lic = self.sel.by_answers({'foo':'bar', 'rofl':'lolcats'})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Public Domain'
        lic2 = self.sel.by_code('publicdomain')
        assert lic == lic2

