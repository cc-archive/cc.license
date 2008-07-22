
import nose.tools
from zope.interface import implementedBy

import cc.license
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib.exceptions import CCLicenseError
from cc.license.lib import all_possible_answers

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

    def test_empty_answers(self):
        nose.tools.assert_raises(CCLicenseError, self.sel.by_answers, {})

    def test_nonsense_answers(self):
        nose.tools.assert_raises(CCLicenseError, self.sel.by_answers,
                                 {'commercial':'foo', 'derivatives':'bar'})

    def test_extra_answers(self):
        lic = self.sel.by_answers({'commercial':'y',
                                   'derivatives':'y',
                                   'foo':'bar',
                                   'lolcats':'roflcopter'})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Attribution'
        lic2 = self.sel.by_code('by')
        assert lic == lic2

    def test_all(self):
        known_bad = []
        bad_jurisdictions = ['ec', 'no', # licenses don't exist
                             'fi', # weird ordering exception
                            ]
        for answer_dict in all_possible_answers(self.sel.questions()):
            if answer_dict in known_bad or \
               answer_dict['jurisdiction'] in bad_jurisdictions:
                continue
            print answer_dict
            lic = self.sel.by_answers(answer_dict)
            assert type(lic) == cc.license.License


class TestAnswersSampling:

    def __init__(self):
        self.sel = cc.license.selectors.choose('recombo')

    def test_no_answers(self):
        nose.tools.assert_raises(CCLicenseError, self.sel.by_answers, {})

    def test_invalid_answers(self):
        nose.tools.assert_raises(CCLicenseError, self.sel.by_answers,
                                 {'sampling':'roflcopter'})

    def test_extra_answers(self):
        lic = self.sel.by_answers({'sampling':'sampling',
                                   'foo':'bar',
                                   'lolcats':'roflcopter'})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Sampling'
        lic2 = self.sel.by_code('sampling')
        assert lic == lic2

    def test_all(self):
        known_bad = [dict(jurisdiction='br', sampling='ncsamplingplus')]
        for answer_dict in all_possible_answers(self.sel.questions()):
            if answer_dict in known_bad:
                continue
            lic = self.sel.by_answers(answer_dict)
            assert type(lic) == cc.license.License

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
