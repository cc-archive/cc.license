"""Unit tests and functional tests exercising cc.license._lib"""
from builtins import object

import nose.tools
import cc.license
from cc.license import CCLicenseError
import cc.license._lib as lib


class TestUriDict(object):

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

class TestFunctions(object):

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

def test_jurisdictions_for_selector():
    """
    Test for rdf_helper.jurisdictions_for_selector
    """
    # Presumably, we won't be adding sampling licenses, so this test
    # might be pretty stable :)
    nose.tools.assert_equal(
        lib.rdf_helper.jurisdictions_for_selector(
            'http://creativecommons.org/license/sampling/'),
        set(['http://creativecommons.org/international/br/',
             'http://creativecommons.org/international/de/',
             'http://creativecommons.org/international/tw/']))
            
    # CC0 is international!  No jurisdictions!  Shouldn't have anything.
    nose.tools.assert_equal(
        lib.rdf_helper.jurisdictions_for_selector(
            'http://creativecommons.org/choose/mark/'),
        set())


def test_sort_licenses():
    lic1 = cc.license.by_code('by', version='1.0')
    lic2 = cc.license.by_code('by', version='2.0')
    lic2_5 = cc.license.by_code('by', version='2.5')
    lic3 = cc.license.by_code('by', version='3.0')

    licenses = [lic2, lic1, lic3, lic2_5]
    licenses.sort(lib.functions.sort_licenses)
    assert licenses == [lic1, lic2, lic2_5, lic3]


def test_all_possible_license_versions():
    """
    Make sure all_possible_license_versions works
    """
    license_uris = [
        lic.uri
        for lic in lib.all_possible_license_versions('by')]

    nose.tools.assert_equal(
        license_uris,
        ['http://creativecommons.org/licenses/by/1.0/',
         'http://creativecommons.org/licenses/by/2.0/',
         'http://creativecommons.org/licenses/by/2.5/',
         'http://creativecommons.org/licenses/by/3.0/'])

    license_uris = [
        lic.uri
        for lic in lib.all_possible_license_versions('by-sa', 'es')]

    nose.tools.assert_equal(
        license_uris,
        ['http://creativecommons.org/licenses/by-sa/2.0/es/',
         'http://creativecommons.org/licenses/by-sa/2.1/es/',
         'http://creativecommons.org/licenses/by-sa/2.5/es/',
         'http://creativecommons.org/licenses/by-sa/3.0/es/'])
    

def test_get_license_legalcodes():
    """
    Test rdf_helper.get_license_legalcodes()
    """
    # One-legalcode
    nose.tools.assert_equal(
        lib.rdf_helper.get_license_legalcodes(
            'http://creativecommons.org/licenses/by/2.5/'),
        set([('http://creativecommons.org/licenses/by/2.5/legalcode', None)]))

    # Multi(language)-legalcode
    expected = set(
        [('http://creativecommons.org/licenses/by/2.5/es/legalcode.ca', 'ca'),
         ('http://creativecommons.org/licenses/by/2.5/es/legalcode.es', 'es'),
         ('http://creativecommons.org/licenses/by/2.5/es/legalcode.eu', 'eu'),
         ('http://creativecommons.org/licenses/by/2.5/es/legalcode.gl', 'gl')])
    result = lib.rdf_helper.get_license_legalcodes(
        'http://creativecommons.org/licenses/by/2.5/es/')
    nose.tools.assert_equal(result, expected)
