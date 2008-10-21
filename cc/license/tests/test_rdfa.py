"""Unit tests utilizing RDFa parsing. Primarily cc.license.formatter."""

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

    def parse(self, rdfa_string):
        return self.parser.parse_string(rdfa_string, self.base)

    def test_basic(self):
        r = self.fmtr.format(self.lic)
        trips = self.parse(r)
        assert self.lic.uri in trips[self.base][str(self.w3.license)]
