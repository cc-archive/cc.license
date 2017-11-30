from future import standard_library
standard_library.install_aliases()
import io

from lxml import etree
from nose.tools import assert_equal

from cc.license import util


UNSTRIPPED_TEMPLATE_OUTPUT = u""" <html xmlns="http://www.w3.org/1999/xhtml" xmlns:dc="http://purl.org/dc/elements/1.1/title">
  <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">
    <img alt="Creative Commons License" style="border-width:0" />
  </a>
  <br />

  
  <span xmlns:dc="http://purl.org/dc/elements/1.1/" property="dc:title" rel="dc:type" href="http://purl.org/dc/dcmitype/StillImage">TITLE</span>
  
  by
  <a xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName" rel="cc:attributionURL" href="ATTR_URL">ATTR_NAME</a>
  is licensed under a
  <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">
    Creative Commons
    Attribution
    3.0
    Unported
    License
  </a>.

</html>
"""

EXPECTED_STRIPPED_OUTPUT = '<a rel="license" href="http://creativecommons.org/licenses/by/3.0/"><img alt="Creative Commons License" style="border-width:0"/></a><br/><span xmlns:dc="http://purl.org/dc/elements/1.1/" property="dc:title" rel="dc:type" href="http://purl.org/dc/dcmitype/StillImage">TITLE</span> by <a xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName" rel="cc:attributionURL" href="ATTR_URL">ATTR_NAME</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution 3.0 Unported License</a>.'


SIMPLE_XHTML = (
    '<html xmlns="http://www.w3.org/1999/xhtml" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/title">'
    '<h1 xmlns:dc="http://purl.org/dc/elements/1.1/" property="dc:title">'
    'Welcome to the best blog</h1>'
    '<p>Hello and <b>welcome</b> to my blog!<br /> '
    'You know, and stuff.</p><p>test!</p></html>')
EXPECTED_INNER_XHTML = (
    '<h1 xmlns:dc="http://purl.org/dc/elements/1.1/" property="dc:title">'
    'Welcome to the best blog</h1>'
    '<p>Hello and <b>welcome</b> to my blog!<br /> '
    'You know, and stuff.</p><p>test!</p>')


def test_simple_inner_xhtml_namespacing():
    inner_xhtml_result = util.inner_xml(SIMPLE_XHTML)
    assert_equal(inner_xhtml_result, EXPECTED_INNER_XHTML)


def test_output_stripping():
    stripped_output = util.stripped_inner_xml(UNSTRIPPED_TEMPLATE_OUTPUT)
    assert_equal(stripped_output, EXPECTED_STRIPPED_OUTPUT)


def test_locale_dict_fetch_with_fallbacks():
    data_dict = {
        'de-ch': 'de-ch value',
        'de': 'de value',
        'en': 'en value',
        None: 'None value',
        'unused': 'we do not use this'}

    assert_equal(
        util.locale_dict_fetch_with_fallbacks(
            data_dict, 'de-ch'), 'de-ch value')
    data_dict.pop('de-ch')

    assert_equal(
        util.locale_dict_fetch_with_fallbacks(
            data_dict, 'de-ch'), 'de value')
    data_dict.pop('de')

    assert_equal(
        util.locale_dict_fetch_with_fallbacks(
            data_dict, 'de-ch'), 'en value')
    data_dict.pop('en')

    assert_equal(
        util.locale_dict_fetch_with_fallbacks(
            data_dict, 'de-ch'), 'None value')

def test_escape():
    assert util.escape('\'"<>&') == '&#39;&#34;&lt;&gt;&amp;'
