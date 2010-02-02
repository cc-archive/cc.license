
import nose.tools
from zope.interface import implementedBy
import os

import rdfadict

import cc.license
from cc.license import CCLicenseError
from cc.license._lib.interfaces import ILicenseFormatter
from cc.license.tests import relax_validate, RELAX_PATH

RELAX_HTML = os.path.join(RELAX_PATH, 'html_rdfa.relax.xml')

def test_list_formatters():
    """Test that we can get a list of formatter strings."""
    formatters = cc.license.formatters.list()
    assert type(formatters) == list
    for f in formatters:
        assert type(f) == str

def test_get_formatter():
    """formatters.choose() must return a valid IFormatter for each formatter."""
    for formatter_id in cc.license.formatters.list():
        f = cc.license.formatters.choose(formatter_id)
        assert ILicenseFormatter in implementedBy(f.__class__)
        f2 = cc.license.formatters.choose(formatter_id)
        assert f2 is f # singletons
    
def test_get_formatter_key_error():
    """formatters.choose() should raise a CCLicenseError if supplied 
       with an invalid formatter id."""
    nose.tools.assert_raises(CCLicenseError,
                             cc.license.formatters.choose, 'roflcopter')

class TestHTMLFormatter:

    def __init__(self):
        self.lic = cc.license.by_code('by')
        self.html = cc.license.formatters.HTML

    # XXX not wrapped in <html> tags
    def _validate(self, output):
        relax_validate(RELAX_HTML, '<html>' + output + '</html>')

    def test_basic(self):
        output = self.html.format(self.lic, locale='en')
        self._validate(output)

    def test_work_format(self):
        for format in ('Audio', 'Video', 'Image', 'Text', 'Interactive'):
            work_dict = {'format':format}
            output = self.html.format(self.lic, work_dict=work_dict)
            self._validate(output)

    def test_invalid_work_format(self):
        work_dict = {'format':'roflcopter'}
        output = self.html.format(self.lic, work_dict=work_dict)
        self._validate(output)


EXPECTED_CC0_PLAIN = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span>
  with this work has waived all copyright and related or neighboring
  rights to this work.
</p>"""

EXPECTED_CC0_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span> with
  Expected Title has waived all copyright and related or
  neighboring rights
  to <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_ACTOR = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="[_:publisher]" rel="dct:publisher"><span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  this work.
</p>"""

EXPECTED_CC0_ACTOR_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="[_:publisher]" rel="dct:publisher"><span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_LINK = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="http://example.org/expected_url" rel="dct:publisher">http://example.org/expected_url</a>
  has waived all copyright and related or neighboring rights to
  this work.
</p>"""

EXPECTED_CC0_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="http://example.org/expected_url" rel="dct:publisher">http://example.org/expected_url</a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""


EXPECTED_CC0_ACTOR_AND_LINK = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="http://example.org/expected_url" rel="dct:publisher"><span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  this work.
</p>
"""

EXPECTED_CC0_ACTOR_AND_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="http://example.org/expected_url" rel="dct:publisher"><span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_COUNTRY = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span>
  with this work has waived all copyright and related or neighboring
  rights to this work.
This work is published from
<span about="" property="vcard:Country" datatype="dct:ISO3166" content="AU">Australia</span>.
</p>"""

EXPECTED_CC0_COUNTRY_ACTOR_AND_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license" style="text-decoration:none;"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" border="0" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a href="http://example.org/expected_url" rel="dct:publisher"><span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
This work is published from
<span about="http://example.org/expected_url" property="vcard:Country" datatype="dct:ISO3166" content="AU">Australia</span>.
</p>"""

class TestCC0Formatter:
    def __init__(self):
        self.license = cc.license.by_code('CC0')
        self.html = cc.license.formatters.classes.CC0HTMLFormatter()

    # XXX not wrapped in <html> tags
    def _validate(self, output):
        assert 0
        relax_validate(RELAX_HTML, '<html>' + output + '</html>')

    def test_plain(self):
        output = self.html.format(self.license, locale='en')
        assert output.strip() == EXPECTED_CC0_PLAIN

    def test_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title'})
        assert output.strip() == EXPECTED_CC0_TITLE

    def test_actor(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'actor': 'Expected Name'})
        assert output.strip() == EXPECTED_CC0_ACTOR

    def test_actor_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'actor': 'Expected Name'})
        assert output.strip() == EXPECTED_CC0_ACTOR_TITLE

    def test_link(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'actor_href': 'http://example.org/expected_url'})
        assert output.strip() == EXPECTED_CC0_LINK

    def test_link_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'actor_href': 'http://example.org/expected_url'})
        assert output.strip() == EXPECTED_CC0_LINK_TITLE

    def test_actor_link(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'actor': 'Expected Name',
                'actor_href': 'http://example.org/expected_url'})
        assert output.strip() == EXPECTED_CC0_ACTOR_AND_LINK

    def test_actor_link_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'actor': 'Expected Name',
                'actor_href': 'http://example.org/expected_url'})
        assert output.strip() == EXPECTED_CC0_ACTOR_AND_LINK_TITLE
        
    def test_country(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_jurisdiction': 'AU'})
        assert output.strip() == EXPECTED_CC0_COUNTRY

    def test_country_actor_link_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'actor': 'Expected Name',
                'actor_href': 'http://example.org/expected_url',
                'work_jurisdiction': 'AU'})
        assert output.strip() == EXPECTED_CC0_COUNTRY_ACTOR_AND_LINK_TITLE


class TestPublicApi:

    def __init__(self):
        self.dir = dir(cc.license.formatters)

    def test_aliased_formatters(self):
        assert 'HTML' in self.dir

    def test_functions(self):
        for f in ('choose', 'list'):
            assert f in self.dir


class TestFilters:

    def __init__(self):
        self.lic = cc.license.by_code('by')
        self.parser = rdfadict.RdfaParser()

    def _get_triples(self, work_dict):
        formatted_html = cc.license.formatters.HTML.format(self.lic, work_dict)

        return self.parser.parse_string(
            formatted_html, "http://example.org/testing")

    def test_permissions_presence(self):
        triples = self._get_triples({'more_permissions_url':'ASDFASDF'})

        result = triples["http://example.org/testing"].get(
            "http://creativecommons.org/ns#morePermissions")
        assert result == ["http://example.org/ASDFASDF"]

    def test_permissions_absence(self):
        triples = self._get_triples({})

        result = triples["http://example.org/testing"].get(
            "http://creativecommons.org/ns#morePermissions")
        assert result != ["http://example.org/ASDFASDF"]

    def test_source_presence(self):
        triples = self._get_triples({'source_work':'ASDFASDF'})

        result = triples["http://example.org/testing"].get(
            "http://purl.org/dc/elements/1.1/source")
        assert result == ["http://example.org/ASDFASDF"]

    def test_source_absence(self):
        triples = self._get_triples({})

        result = triples["http://example.org/testing"].get(
            "http://purl.org/dc/elements/1.1/source")
        assert result != ["http://example.org/ASDFASDF"]


class TestCustomization:

    def __init__(self):
        self.formatters = []
        for s in cc.license.formatters.list():
            self.formatters.append(cc.license.formatters.choose(s))

    def test_repr(self):
        for f in self.formatters:
            r = repr(f)
            assert f.id in r
            assert r.startswith('<')
            assert r.endswith('>')

    def test_str(self):
        for f in self.formatters:
            s = str(f)
            assert f.title in s


#####
# CC0
#####

