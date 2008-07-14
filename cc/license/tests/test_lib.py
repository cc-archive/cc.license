"""Unit tests and functional tests exercising cc.license.lib"""

import nose.tools
import cc.license.lib as lib
from cc.license.lib.exceptions import CCLicenseError

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
                    )
        self.dicts = (
                   dict(code='by-nc', version='2.0', jurisdiction='tw'),
                   dict(code='by-sa', version='3.0'),
                   dict(code='by'),
                     )

    def test_uri_commutativity(self):
        for uri in self.uris:
            assert uri == lib.dict2uri(lib.uri2dict(uri))

    # TODO: this is a harder test to write
    #def test_dict_commutivity(self):
    #    pass

    def test_malformed_uri(self):
        for m in self.malformed:
            nose.tools.assert_raises(CCLicenseError, lib.uri2dict, m)
