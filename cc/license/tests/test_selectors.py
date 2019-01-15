from builtins import str
from builtins import object

import nose.tools

import cc.license
from cc.license import CCLicenseError
from cc.license._lib import all_possible_answers

def test_list_selectors():
    """Test that we can get a list of selector strings."""
    selectors = cc.license.selectors.list()
    assert type(selectors) == list
    for s in selectors:
        assert type(s) == str

def test_get_selector():
    """selectors.choose() must return a valid ISelector for each selector."""
    for selector_id in cc.license.selectors.list():
        s = cc.license.selectors.choose(selector_id)
        s2 = cc.license.selectors.choose(selector_id)
        assert s2 is s # singletons, in a way

def test_id_and_uri():
    for sid in cc.license.selectors.list():
        s = cc.license.selectors.choose(sid)

        assert ('http://creativecommons.org/license' in s.uri) or \
                ('http://creativecommons.org/choose' in s.uri)

def test_get_selector_key_error():
    """selectors.choose() should raise a CCLicenseError if supplied 
       with an invalid selector id."""
    assert cc.license.selectors.choose('roflcopter') == None

def test_has_license():
    std = cc.license.selectors.choose('standard')
    has = 'http://creativecommons.org/licenses/by/3.0/'
    hasnt = 'roflcopter'
    assert std.has_license(has)
    assert not std.has_license(hasnt)
    # multiple times, to check caching
    assert std.has_license(has)
    assert not std.has_license(hasnt)
    assert std.has_license(has)
    assert not std.has_license(hasnt)

def test_functional_one():
    std = cc.license.selectors.choose('standard')
    uri = 'http://creativecommons.org/licenses/by-nc/3.0/'
    assert std.has_license(uri)
    by_nc = std.by_uri(uri)
    assert std.has_license(uri)
    assert by_nc == std.by_uri(uri)
    # double-check
    assert type(std.by_uri(uri)) == cc.license.License
    assert std.has_license(uri)


class TestIssuers(object):

    def __init__(self):
        self.std = cc.license.selectors.choose('standard')
        self.uris = (
                     'http://creativecommons.org/licenses/by/3.0/us/',
                     'http://creativecommons.org/licenses/by-nc-nd/2.1/jp/',
                     'http://creativecommons.org/licenses/by-nc-sa/2.5/mx/',
                     'http://creativecommons.org/licenses/by-sa/2.0/de/',
                    )
        self.bad_uris = (
                         'http://creativecommons.com/licenses/by/3.0/us/',
                         'http://creativemonkeys.org/licenses/by/3.0/us/',
                         'jdsalfkjalskdjfa;lskdjfalsdjf;laskdf',
                         'roflcopter thundercats',
                         'http://',
                         '',
                        )

    def test_by_uri(self):
        for u in self.uris:
            lic = self.std.by_uri(u)
            assert type(lic) == cc.license.License

    def test_by_uri_fails(self):
        for b in self.bad_uris:
            assert self.std.by_uri(b) == None

    # TODO: test by_code

class TestQuestions(object):

    def __init__(self):
        self.std = cc.license.selectors.choose('standard')
        self.pd = cc.license.selectors.choose('publicdomain')

    def test_standard_questions(self):
        questions = self.std.questions()
        assert type(questions) == list
        assert len(questions) != 0
        for q in questions:
            assert type(q) in (
                cc.license.Question, cc.license.JurisdictionQuestion)

    def test_publicdomain_questions(self):
        questions = self.pd.questions()
        assert type(questions) == list
        assert len(questions) == 0

class TestAnswersStandard(object):

    def __init__(self):
        self.sel = cc.license.selectors.choose('standard')

    def test_empty_answers(self):
        assert self.sel.by_answers({}) == None

    def test_nonsense_answers(self):
        assert self.sel.by_answers(
            {'commercial':'foo', 'derivatives':'bar'}) == None

    def test_extra_answers(self):
        lic = self.sel.by_answers({'commercial':'y',
                                   'derivatives':'y',
                                   'foo':'bar',
                                   'lolcats':'roflcopter'})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Attribution 4.0 International'
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
            lic = self.sel.by_answers(answer_dict)
            assert type(lic) == cc.license.License

    def test_sa_upwards_compatibility_correction(self):
        """
        1.0 SA licenses don't have upwards compatibility, so we
        shouldn't issue them.
        """
        # fi BY-SA license is 1.0 only, so issue unported instead
        license = self.sel.by_answers(
            {'commercial': 'y', 'derivatives': 'sa', 'jurisdiction': 'fi'})
        assert license.uri == 'http://creativecommons.org/licenses/by-sa/4.0/'

        # Don't correct where unnecessary though
        license = self.sel.by_answers(
            {'commercial': 'y', 'derivatives': 'sa', 'jurisdiction': 'es'})
        assert license.uri == 'http://creativecommons.org/licenses/by-sa/3.0/es/'


class TestAnswersSampling(object):

    def __init__(self):
        self.sel = cc.license.selectors.choose('recombo')

    def test_no_answers(self):
        assert self.sel.by_answers({}) == None

    def test_invalid_answers(self):
        assert self.sel.by_answers({'sampling':'roflcopter'}) == None

    def test_extra_answers(self):
        lic = self.sel.by_answers({'sampling':'sampling',
                                   'foo':'bar',
                                   'lolcats':'roflcopter'})
        assert type(lic) == cc.license.License
        assert lic.title() == 'Sampling 1.0'
        lic2 = self.sel.by_code('sampling')
        assert lic == lic2

    def test_all(self):
        known_bad = [dict(jurisdiction='br', sampling='ncsamplingplus'),
                     dict(jurisdiction='de', sampling='ncsamplingplus'),
                     dict(jurisdiction='de', sampling='sampling')]
        for answer_dict in all_possible_answers(self.sel.questions()):
            if answer_dict in known_bad:
                continue
            lic = self.sel.by_answers(answer_dict)
            assert type(lic) == cc.license.License

class TestAnswersPublicdomain(object):

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


class TestPublicApi(object):

    def __init__(self):
        self.dir = dir(cc.license.selectors)

    def test_functions(self):
        for f in ('choose', 'list'):
            assert f in self.dir


class TestCustomization(object):

    def __init__(self):
        self.sels = []
        for s in cc.license.selectors.list():
            self.sels.append(cc.license.selectors.choose(s))

    def test_repr(self):
        for ls in self.sels:
            r = repr(ls)
            assert ls.id in r
            assert 'LicenseSelector' in r
            assert r.startswith('<')
            assert r.endswith('>')

    def test_str(self):
        for ls in self.sels:
            s = str(ls)
            assert ls.title() in s
