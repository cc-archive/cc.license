
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


EXPECTED_CC0_PLAIN = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span>
  with this work has waived all copyright and related or neighboring
  rights to this work.
</p>"""

EXPECTED_CC0_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span>
  with
  Expected Title
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_ACTOR = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span resource="[_:publisher]" rel="dct:publisher">
    <span property="dct:title">Expected Name</span></span>
  has waived all copyright and related or neighboring rights to
  this work.
</p>"""

EXPECTED_CC0_ACTOR_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span resource="[_:publisher]" rel="dct:publisher">
    <span property="dct:title">Expected Name</span></span>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_LINK = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://example.org/expected_url">http://example.org/expected_url</a>
  has waived all copyright and related or neighboring rights to
  this work.
</p>"""

EXPECTED_CC0_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://example.org/expected_url">http://example.org/expected_url</a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""


EXPECTED_CC0_ACTOR_AND_LINK = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://example.org/expected_url">
    <span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  this work.
</p>"""

EXPECTED_CC0_ACTOR_AND_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://example.org/expected_url">
    <span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
</p>"""

EXPECTED_CC0_COUNTRY = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <span rel="dct:publisher" resource="[_:publisher]">the person who associated CC0</span>
  with this work has waived all copyright and related or neighboring
  rights to this work.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
      content="AU" about="[_:publisher]">
  Australia</span>.
</p>"""

EXPECTED_CC0_COUNTRY_ACTOR_AND_LINK_TITLE = """<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/l/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://example.org/expected_url">
    <span property="dct:title">Expected Name</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Expected Title</span>.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
      content="AU" about="http://example.org/expected_url">
  Australia</span>.
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
                'name': 'Expected Name'})
        assert output.strip() == EXPECTED_CC0_ACTOR

    def test_actor_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'name': 'Expected Name'})
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
                'name': 'Expected Name',
                'actor_href': 'http://example.org/expected_url'})
        assert output.strip() == EXPECTED_CC0_ACTOR_AND_LINK

    def test_actor_link_title(self):
        output = self.html.format(
            self.license, locale='en',
            work_dict={
                'work_title': 'Expected Title',
                'name': 'Expected Name',
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
                'name': 'Expected Name',
                'actor_href': 'http://example.org/expected_url',
                'work_jurisdiction': 'AU'})
        assert output.strip() == EXPECTED_CC0_COUNTRY_ACTOR_AND_LINK_TITLE


EXPECTED_PDMARK_PLAIN = """<p>
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_WORKTITLE = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (<span property="dct:title">WORK TITLE</span>) is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_AUTHOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (by <a href="AUTHOR_URL" rel="dct:creator"><span property="dct:title">AUTHOR</span></a>) is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_AUTHOR_NOLINK = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (by <span resource="[_:creator]" rel="dct:creator"><span property="dct:title">AUTHOR</span></span>) is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_AUTHOR_ONLYLINK = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (by <a href="AUTHOR_URL" rel="dct:creator">AUTHOR_URL</a>) is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_CURATOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work, identified by <a href="CURATOR_URL" rel="dct:publisher"><span property="dct:title">CURATOR</span></a>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_CURATOR_NOLINK = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work, identified by <span resource="[_:publisher]" rel="dct:publisher"><span property="dct:title">CURATOR</span></span>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_CURATOR_ONLYLINK = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work, identified by <a href="CURATOR_URL" rel="dct:publisher">CURATOR_URL</a>, is free of known copyright restrictions.
</p>"""


EXPECTED_PDMARK_WORKTITLE_AUTHOR_CURATOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (<span property="dct:title">WORK TITLE</span>, by <a href="AUTHOR_URL" rel="dct:creator"><span property="dct:title">AUTHOR</span></a>), identified by <a href="CURATOR_URL" rel="dct:publisher"><span property="dct:title">CURATOR</span></a>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_WORKTITLE_AUTHOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (<span property="dct:title">WORK TITLE</span>, by <a href="AUTHOR_URL" rel="dct:creator"><span property="dct:title">AUTHOR</span></a>) is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_WORKTITLE_CURATOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (<span property="dct:title">WORK TITLE</span>), identified by <a href="CURATOR_URL" rel="dct:publisher"><span property="dct:title">CURATOR</span></a>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_AUTHOR_CURATOR = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (by <a href="AUTHOR_URL" rel="dct:creator"><span property="dct:title">AUTHOR</span></a>), identified by <a href="CURATOR_URL" rel="dct:publisher"><span property="dct:title">CURATOR</span></a>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_CC0 = """<p>
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/">
<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"
     style="border-style: none;" alt="CC0" />
</a>
<br />
This work is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_WORKTITLE_AUTHOR_CURATOR_CC0 = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/">
<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"
     style="border-style: none;" alt="CC0" />
</a>
<br />
This work (<span property="dct:title">WORK TITLE</span>, by <a href="AUTHOR_URL" rel="dct:creator"><span property="dct:title">AUTHOR</span></a>), identified by <a href="CURATOR_URL" rel="dct:publisher"><span property="dct:title">CURATOR</span></a>, is free of known copyright restrictions.
</p>"""

EXPECTED_PDMARK_ESCAPETEST = """<p xmlns:dct="http://purl.org/dc/terms/">
<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>
<br />
This work (<span property="dct:title">&lt;b&gt;&#39;HAXX0rs&#39; &amp; &#34;LAMERS&#34;&lt;/b&gt;</span>, by <a href="&lt;b&gt;&#39;HAXX0rs&#39; &amp; &#34;LAMERS&#34;&lt;/b&gt;" rel="dct:creator"><span property="dct:title">&lt;b&gt;&#39;HAXX0rs&#39; &amp; &#34;LAMERS&#34;&lt;/b&gt;</span></a>), identified by <a href="&lt;b&gt;&#39;HAXX0rs&#39; &amp; &#34;LAMERS&#34;&lt;/b&gt;" rel="dct:publisher"><span property="dct:title">&lt;b&gt;&#39;HAXX0rs&#39; &amp; &#34;LAMERS&#34;&lt;/b&gt;</span></a>, is free of known copyright restrictions.
</p>"""


class TestPDMarkFormatter:
    def __init__(self):
        self.formatter = cc.license.formatters.classes.PDMarkHTMLFormatter()
        self.license = cc.license.by_code('mark')

    def test_plain(self):
        output = self.formatter.format(self.license, locale='en')
        assert output.strip() == EXPECTED_PDMARK_PLAIN

    def test_worktitle(self):
        output = self.formatter.format(
            self.license,
            {'work_title': 'WORK TITLE'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_WORKTITLE

    def test_author(self):
        # Normal
        output = self.formatter.format(
            self.license,
            {'author_title': 'AUTHOR',
             'author_href': 'AUTHOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_AUTHOR

        # No link
        output = self.formatter.format(
            self.license,
            {'author_title': 'AUTHOR'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_AUTHOR_NOLINK

        # Only link
        output = self.formatter.format(
            self.license,
            {'author_href': 'AUTHOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_AUTHOR_ONLYLINK

    def test_curator(self):
        # Normal
        output = self.formatter.format(
            self.license,
            {'curator_title': 'CURATOR',
             'curator_href': 'CURATOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_CURATOR

        # No link
        output = self.formatter.format(
            self.license,
            {'curator_title': 'CURATOR'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_CURATOR_NOLINK

        # Only link
        output = self.formatter.format(
            self.license,
            {'curator_href': 'CURATOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_CURATOR_ONLYLINK

    def test_worktitle_author_curator(self):
        output = self.formatter.format(
            self.license,
            {'work_title': 'WORK TITLE',
             'author_title': 'AUTHOR',
             'author_href': 'AUTHOR_URL',
             'curator_title': 'CURATOR',
             'curator_href': 'CURATOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_WORKTITLE_AUTHOR_CURATOR
        
    def test_worktitle_author(self):
        output = self.formatter.format(
            self.license,
            {'work_title': 'WORK TITLE',
             'author_title': 'AUTHOR',
             'author_href': 'AUTHOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_WORKTITLE_AUTHOR

    def test_worktitle_curator(self):
        output = self.formatter.format(
            self.license,
            {'work_title': 'WORK TITLE',
             'curator_title': 'CURATOR',
             'curator_href': 'CURATOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_WORKTITLE_CURATOR

    def test_author_curator(self):
        output = self.formatter.format(
            self.license,
            {'author_title': 'AUTHOR',
             'author_href': 'AUTHOR_URL',
             'curator_title': 'CURATOR',
             'curator_href': 'CURATOR_URL'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_AUTHOR_CURATOR

    def test_cc0(self):
        output = self.formatter.format(
            self.license,
            {'waive_cc0': True},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_CC0

        output = self.formatter.format(
            self.license,
            {'work_title': 'WORK TITLE',
             'author_title': 'AUTHOR',
             'author_href': 'AUTHOR_URL',
             'curator_title': 'CURATOR',
             'curator_href': 'CURATOR_URL',
             'waive_cc0': True},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_WORKTITLE_AUTHOR_CURATOR_CC0

    def test_escaping(self):
        output = self.formatter.format(
            self.license,
            {'work_title': '<b>\'HAXX0rs\' & "LAMERS"</b>',
             'author_title': '<b>\'HAXX0rs\' & "LAMERS"</b>',
             'author_href': '<b>\'HAXX0rs\' & "LAMERS"</b>',
             'curator_title': '<b>\'HAXX0rs\' & "LAMERS"</b>',
             'curator_href': '<b>\'HAXX0rs\' & "LAMERS"</b>'},
            locale='en')
        assert output.strip() == EXPECTED_PDMARK_ESCAPETEST


EXPECTED_PUBLICDOMAIN_PLAIN = (
    '<a rel="license" href="http://creativecommons.org/licenses/publicdomain/">'
    '<img alt="Creative Commons License" style="border-width:0"'
    ' src="http://i.creativecommons.org/l/publicdomain/88x31.png" /></a><br />'
    'This work is in the '
    '<a rel="license" href="http://creativecommons.org/licenses/publicdomain/">'
    'Public Domain</a>.')

EXPECTED_PUBLICDOMAIN_WORKFORMAT = (
    '<a rel="license" href="http://creativecommons.org/licenses/publicdomain/">'
    '<img alt="Creative Commons License" style="border-width:0"'
    ' src="http://i.creativecommons.org/l/publicdomain/88x31.png" /></a><br />'
    'This <span xmlns:dct="http://purl.org/dc/terms/"'
    ' href="http://purl.org/dc/dcmitype/MovingImage" rel="dct:type">work</span> '
    'is in the '
    '<a rel="license" href="http://creativecommons.org/licenses/publicdomain/">'
    'Public Domain</a>.')


def test_publicdomain_formatter():
    formatter = cc.license.formatters.classes.PublicDomainHTMLFormatter()
    #####

    license = cc.license.by_code('publicdomain')

    plain_result = formatter.format(
        license, {'format': ''}, 'en')
    assert plain_result == EXPECTED_PUBLICDOMAIN_PLAIN

    # not passing in anything for the work_dict should also give us
    # the "plain" result
    plain_result = formatter.format(
        license, locale='en')
    assert plain_result == EXPECTED_PUBLICDOMAIN_PLAIN

    workformat_result = formatter.format(
        license, {'format': 'MovingImage'}, 'en')
    assert workformat_result == EXPECTED_PUBLICDOMAIN_WORKFORMAT

    # XXX: This isn't officially supported on the old engine, but we
    # should probably add a test for it, since we do?
    # lang_es_result = formatter.format(
    #     license, {'format': ''}, 'es')


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
            "http://purl.org/dc/terms/source")
        assert result == ["http://example.org/ASDFASDF"]

    def test_source_absence(self):
        triples = self._get_triples({})

        result = triples["http://example.org/testing"].get(
            "http://purl.org/dc/terms/source")
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
