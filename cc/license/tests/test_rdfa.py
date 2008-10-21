"""Unit tests utilizing RDFa parsing. Primarily for cc.license.formatter."""

import cc.license
import rdfadict
import rdflib

class TestHtmlFormatter:

    def __init__(self):
        self.parser = rdfadict.RdfaParser()
        self.base = 'http://www.example.com/'
        self.lic = cc.license.by_code('by')
        self.fmtr = cc.license.formatters.HTML
        # define namespaces
        self.w3 = rdflib.Namespace('http://www.w3.org/1999/xhtml/vocab#')
        self.dc = rdflib.Namespace('http://purl.org/dc/elements/1.1/')
        self.dc_type = rdflib.Namespace('http://purl.org/dc/dcmitype/')

    def parse(self, rdfa_string):
        return self.parser.parse_string(rdfa_string, self.base)

    def test_basic(self):
        r = self.fmtr.format(self.lic)
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)]

    def test_work_format(self):
        r = self.fmtr.format(self.lic, {'format':'Text'})
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)] # basic
        assert str(self.dc_type.Text) in trips[self.base][str(self.dc.type)]
