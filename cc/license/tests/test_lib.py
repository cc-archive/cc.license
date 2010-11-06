"""Unit tests and functional tests exercising cc.license._lib"""

import nose.tools
import cc.license
from cc.license import CCLicenseError
import cc.license._lib as lib


class TestUriDict:

    def __init__(self):
        self.malformed = (
                          'http://creativecommons.com/licenses',
                          'lorem ipsum dolor sit amet',
                          'http://asdfasdf',
                          'http://creativecommons.org/licenses/by/3.0',
                              # no trailing slash!
                         )
        self.uris = ('http://creativecommons.org/licenses/by-nc/2.0/tw/',
                     'http://creativecommons.org/licenses/by/3.0/',
                     'http://creativecommons.org/licenses/by-sa/2.5/mx/',
                     'http://creativecommons.org/publicdomain/zero/1.0/')
        self.dicts = (
                   dict(code='by-nc', version='2.0', jurisdiction='tw'),
                   dict(code='by-sa', version='3.0'),
                   dict(code='by'),
                   dict(code='CC0', version='1.0'),
                   dict(code='CC0'))

    def test_uri_commutativity(self):
        for uri in self.uris:
            assert uri == lib.dict2uri(lib.uri2dict(uri))

    # TODO: this is a harder test to write
    #def test_dict_commutivity(self):
    #    pass

    def test_malformed_uri(self):
        for m in self.malformed:
            nose.tools.assert_raises(CCLicenseError, lib.uri2dict, m)

    def test_dict2uri_nonetype(self):
        d = dict(code='by', version='3.0', jurisdiction=None)
        assert lib.dict2uri(d) == 'http://creativecommons.org/licenses/by/3.0/'
        e = dict(code='by')
        assert lib.dict2uri(e) == 'http://creativecommons.org/licenses/by/3.0/'
        f = dict(code='by-sa', version='1.0')
        assert lib.dict2uri(f) == 'http://creativecommons.org/licenses/by-sa/1.0/'

class TestFunctions:

    def __init__(self):
        self.pairs = (
         ('http://creativecommons.org/licenses/by-nc/2.0/tw/', 'by-nc'),
         ('http://creativecommons.org/licenses/by/3.0/', 'by'),
         ('http://creativecommons.org/licenses/by-sa/2.5/mx/', 'by-sa'),
         ('http://creativecommons.org/publicdomain/zero/1.0/', 'CC0'),
         
                    )
        self.apl = lib.all_possible_answers # aliasing for brevity

    def test_code_from_uri(self):
        for uri, code in self.pairs:
            assert lib.code_from_uri(uri) == code

    def test_code_from_uri_fails(self):
        nose.tools.assert_raises(CCLicenseError, lib.code_from_uri,
                                 'roflcopter')

    def test_current_version(self):
        for j in ('us', 'de', 'jp', 'uk', 'es'):
            assert type(lib.current_version('by', jurisdiction=j)) == str
        assert lib.current_version('by', jurisdiction='us') == '3.0'
        assert lib.current_version('by-sa', jurisdiction='mx') == '2.5'
        assert lib.current_version('by-nc', jurisdiction='uk') == '2.0'
        assert lib.current_version('CC0') == '1.0'

    def test_current_version_fails(self):
        assert lib.current_version('by-nc-nd', jurisdiction='jo') == ''

    def test_all_possible_answers(self):
        sels = [ cc.license.selectors.choose(s)
                 for s in ('standard', 'recombo', 'publicdomain') ]
        for sel in sels:
            all_answers = self.apl(sel.questions())
            for adict in all_answers:
                for k in [q.id for q in sel.questions()]:
                    assert k in adict
                for q in sel.questions():
                    assert adict[q.id] in \
                           [ a[1] for a in q.answers() ]

    def test_all_possible_answers_publicdomain(self):
        pd = cc.license.selectors.choose('publicdomain')
        assert len(self.apl(pd.questions())) == 1

    def test_apl_doesnt_empty_questions(self):
        """apl should not clobber questions list (previous bug)"""
        std = cc.license.selectors.choose('standard')
        assert std.questions() != 0
        self.apl(std.questions())
        assert std.questions() != 0

    def test_dict2uri_empty_values(self):
        dicts = [
                 dict(jurisdiction=None, version='', code='sampling+'),
                 dict(jurisdiction=None, version=None, code='sampling+'),
                 dict(jurisdiction='', version='', code='sampling+'),
                 dict(jurisdiction='', version=None, code='sampling+')
                ]
        for d in dicts:
            assert lib.dict2uri(d) == \
                   'http://creativecommons.org/licenses/sampling+/1.0/'

def test_get_jurisdiction_languages():
    result = lib.rdf_helper.get_jurisdiction_languages(
        'http://creativecommons.org/international/be/')
    assert set(result) == set(['nl-be', 'fr-be'])
