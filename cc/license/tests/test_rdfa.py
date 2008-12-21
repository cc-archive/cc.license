"""Unit tests utilizing RDFa parsing. Primarily for cc.license.formatter."""

import cc.license
import rdfadict
import rdflib

class TestHtmlFormatter:
    """Class layout and organization:
       There are six properties to be exercised.
       Tests are organized in groups, corresponding to the number
       of properties simultaneously being tested."""

    def __init__(self):
        self.parser = rdfadict.RdfaParser()
        self.base = 'http://www.example.com/'
        self.lic = cc.license.by_code('by')
        self.fmtr = cc.license.formatters.HTML
        # define namespaces
        self.cc = rdflib.Namespace('http://creativecommons.org/ns#')
        self.dc = rdflib.Namespace('http://purl.org/dc/elements/1.1/')
        self.dc_type = rdflib.Namespace('http://purl.org/dc/dcmitype/')
        self.w3 = rdflib.Namespace('http://www.w3.org/1999/xhtml/vocab#')

    def parse(self, rdfa_string):
        return self.parser.parse_string(rdfa_string, self.base)

    # Zero properties (one possible combination; all under test)

    def test_basic(self):
        r = self.fmtr.format(self.lic)
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)]

    # One property (six possible combinations; three under test)

    def test_workformat(self):
        r = self.fmtr.format(self.lic, {'format':'Text'})
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)] # basic
        assert str(self.dc_type.Text) in trips[self.base][str(self.dc.type)]

    def test_worktitle(self):
        r = self.fmtr.format(self.lic, {'worktitle':'TITLE'})
        trips = self.parse(r)
        print trips
        assert 'TITLE' in trips[self.base][str(self.dc['title'])]

    def test_attrname(self):
        r = self.fmtr.format(self.lic, {'attribution_name':'ATTR_NAME'})
        trips = self.parse(r)
        assert 'ATTR_NAME' in trips[self.base][str(self.cc.attributionName)]

    # Two properties (fifteen possible combinations; two under test)

    def test_workformat_worktitle(self):
        r = self.fmtr.format(self.lic, {'format':'Image',
                                        'worktitle':'TITLE'})
        trips = self.parse(r)
        print trips
        assert str(self.dc_type.StillImage) in \
               trips[self.base][str(self.dc.type)]
        assert 'TITLE' in trips[self.base][str(self.dc['title'])]

    def test_attrname_format(self):
        r = self.fmtr.format(self.lic, {'format':'Video',
                                        'attribution_name':'ATTR_NAME'})
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)]
        assert 'ATTR_NAME' in trips[self.base][str(self.cc.attributionName)]
        assert str(self.dc_type.MovingImage) in \
               trips[self.base][str(self.dc.type)]

     # Three properties (twenty possible combinations; zero under test)

     # Four properties (fifteen possible combinations; zero under test)

     # Five properties (six possible combinations; zero under test)

     # Siz properties (one possible combination; zero under test)
