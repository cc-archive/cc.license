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
        self.b = rdflib.Namespace(self.base)

    def parse(self, rdfa_string):
        return self.parser.parse_string(rdfa_string, self.base)

    def parse_trips(self, work_dict={}):
        r = self.fmtr.format(self.lic, work_dict)
        trips = self.parse(r)
        return trips[self.base]

    # Miscellaneous tests
    def test_failing_workformat_with_worktitle(self):
        """Edge case: unknown formats should be ignored"""
        tb = self.parse_trips({'format':'Roflcopter',
                               'worktitle':'TITLE'})
        assert 'TITLE' in tb[str(self.dc['title'])]

    # Zero properties (one possible combination; all under test)

    def test_basic(self):
        tb = self.parse_trips()
        assert self.lic.uri in tb[str(self.w3.license)]

    # One property (five possible combinations; all under test)

    def test_worktitle(self):
        tb = self.parse_trips({'worktitle':'TITLE'})
        assert 'TITLE' in tb[str(self.dc['title'])]

    def test_attrname(self):
        tb = self.parse_trips({'attribution_name':'ATTR_NAME'})
        assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]

    def test_attrurl(self):
        tb = self.parse_trips({'attribution_url':'ATTR_URL'})
        assert str(self.b.ATTR_URL) in tb[str(self.cc.attributionURL)]
        # when alone, URL is also attributionName
        assert 'ATTR_URL' in tb[str(self.cc.attributionName)]

    def test_sourcework(self):
        tb = self.parse_trips({'source_work':'SOURCE_WORK'})
        assert str(self.b.SOURCE_WORK) in tb[str(self.dc.source)]

    def test_morepermissions(self):
        tb = self.parse_trips({'more_permissions_url':'MORE_PERMISSIONS'})
        assert str(self.b.MORE_PERMISSIONS) in tb[str(self.cc.morePermissions)]

    # Two properties (fifteen possible combinations; three under test)

    def test_workformat_worktitle(self):
        tb = self.parse_trips({'format':'Image',
                               'worktitle':'TITLE'})
        assert str(self.dc_type.StillImage) in tb[str(self.dc.type)]
        assert 'TITLE' in tb[str(self.dc['title'])]

    #def test_attrname_format(self):
    #    tb = self.parse_trips({'format':'Video',
    #                           'attribution_name':'ATTR_NAME'})
    #    assert self.lic.uri in tb[str(self.w3.license)]
    #    assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]
    #    assert str(self.dc_type.MovingImage) in \
    #           tb[str(self.dc.type)]

    def test_attrname_attrurl(self):
        tb = self.parse_trips({'attribution_url':'ATTR_URL',
                               'attribution_name':'ATTR_NAME'})
        assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]
        assert str(self.b.ATTR_URL) in tb[str(self.cc.attributionURL)]

    def test_source_more(self):
        tb = self.parse_trips({'source_work':'SOURCE_WORK',
                               'more_permissions_url':'MORE_PERMISSIONS'})
        assert self.lic.uri in tb[str(self.w3.license)]
        assert str(self.b.SOURCE_WORK) in tb[str(self.dc.source)]
        assert str(self.b.MORE_PERMISSIONS) in \
               tb[str(self.cc.morePermissions)]

    # Three properties (twenty possible combinations; two under test)

    def test_an_au_src(self):
        tb = self.parse_trips({'attribution_url':'ATTR_URL',
                               'attribution_name':'ATTR_NAME',
                               'source_work':'SOURCE_WORK'})
        assert self.lic.uri in tb[str(self.w3.license)]
        assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]
        assert str(self.b.ATTR_URL) in tb[str(self.cc.attributionURL)]
        assert str(self.b.SOURCE_WORK) in tb[str(self.dc.source)]

    def test_an_au_mp(self):
        tb = self.parse_trips({'attribution_url':'ATTR_URL',
                               'attribution_name':'ATTR_NAME',
                               'more_permissions_url':'MORE_PERMISSIONS'})
        assert self.lic.uri in tb[str(self.w3.license)]
        assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]
        assert str(self.b.ATTR_URL) in tb[str(self.cc.attributionURL)]
        assert str(self.b.MORE_PERMISSIONS) in \
               tb[str(self.cc.morePermissions)]

    # Four properties (fifteen possible combinations; zero under test)

    def test_an_au_src_mp(self):
        tb = self.parse_trips({'attribution_url':'ATTR_URL',
                               'attribution_name':'ATTR_NAME',
                               'source_work':'SOURCE_WORK',
                               'more_permissions_url':'MORE_PERMISSIONS'})
        assert self.lic.uri in tb[str(self.w3.license)]
        assert 'ATTR_NAME' in tb[str(self.cc.attributionName)]
        assert str(self.b.ATTR_URL) in tb[str(self.cc.attributionURL)]
        assert str(self.b.SOURCE_WORK) in tb[str(self.dc.source)]
        assert str(self.b.MORE_PERMISSIONS) in \
               tb[str(self.cc.morePermissions)]

    # Five properties (six possible combinations; zero under test)

    # Six properties (one possible combination; zero under test)
