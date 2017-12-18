from future import standard_library
standard_library.install_aliases()
from builtins import open, range, str
import csv
import pkg_resources
import re

from lxml import etree
import io


LEFT_WHITE_SPACE_RE = re.compile('\A[ \n\t].*\Z', re.DOTALL)
RIGHT_WHITE_SPACE_RE = re.compile('\A.*[ \n\t]\Z', re.DOTALL)

INNER_XML_RE = re.compile(u'\A[ \n\t]*<[^>]+?>(?P<body>.*)</[^>]+?>[ \n\t]*\Z')


def strip_text(text):
    """
    Takes a bunch of test and removes all possible "indentation gunk"
    from it.

      >>> example_noisy_text = '''
      ...  hey guys
      ...       it looks like 
      ... I am all over the place'''
      >>> strip_text(example_noisy_text)
      u'hey guys it looks like I am all over the place'
    """
    if text:
        return u' '.join(
            [line.strip() for line in text.splitlines() if line.strip()])
    else:
        # return whatever text was, there's nothing to do
        # (prolly None or empty string)
        return text


def strip_xml(element):
    """
    Recursively strip clean indentation from xml.  Especially useful
    if you're using a template.

    For example, this is a bit of a mess:
      >>> xml_mess = '''
      ... <help> How did
      ... 
      ...  <person>I
      ...    </person>
      ... get to be so <cleanliness
      ...     xmlns:clean="http://example.org/howclean/#"
      ...     clean:cleanliness="filthy">messy</cleanliness>?
      ...    </help>  '''

    strip_xml requires that you pass in an element though, so let's
    get the root node and pass it in:

      >>> from lxml import etree
      >>> import StringIO
      >>> etree_mess = etree.parse(StringIO.StringIO(xml_mess))
      >>> cleaned_root_mess = strip_xml(etree_mess.getroot())
      >>> etree.tounicode(cleaned_root_mess)
      '<help>How did <person>I</person> get to be so <cleanliness xmlns:clean="http://example.org/howclean/#" clean:cleanliness="filthy">messy</cleanliness>?</help>'

    Note that strip_xml operates on the mutability of the argument
    `element`, so the object returned is the same object that's passed
    in.

      >>> cleaned_root_mess is etree_mess.getroot()
      True
    """
    def _recursive_strip(elt, childpos, childrenlen):
        orig_text = elt.text or ''
        orig_tail = elt.tail or ''

        children = list(elt)
        new_childrenlen = len(children)

        elt.text = strip_text(elt.text)
        elt.tail = strip_text(elt.tail)

        # We have to do a lot of stuff here to put whitespace in the
        # right places and make it look pretty, as if a human wrote
        # it.

        ##########
        #### whitespace re-appending
        ##########

        ####
        ## left of the .text
        ####
        # pretty much never

        ####
        ## right of the .text
        ####
        # if there are children and is presently whitespace
        if elt.text \
                and new_childrenlen \
                and RIGHT_WHITE_SPACE_RE.match(orig_text):
            elt.text = elt.text + ' '

        ####
        ## left of the .tail
        ####
        # any time there is presently whitespace
        if elt.tail and LEFT_WHITE_SPACE_RE.match(orig_tail):
            elt.tail = ' ' + elt.tail

        ####
        ## right of the .tail
        ####
        # if there is presently whitespace and not the last child
        if elt.tail \
                and RIGHT_WHITE_SPACE_RE.match(orig_tail) \
                and childpos != childrenlen - 1:
            elt.tail = elt.tail + ' '

        for i in range(new_childrenlen):
            child = children[i]
            _recursive_strip(child, i, new_childrenlen)

    _recursive_strip(element, 0, 1)
    return element


def inner_xml(xml_text):
    """
    Get the inner xml of an element.

      >>> inner_xml('<div>This is some <i><b>really</b> silly</i> text!</div>')
      u'This is some <i><b>really</b> silly</i> text!'
    """
    return str(INNER_XML_RE.match(xml_text).groupdict()['body'])


def stripped_inner_xml(xml_string):
    """
    Take a string of xml and both strip whitespace and return its
    inner elements.

    This is a convenience function so you don't have to run strip_xml
    and inner_xml manually.

      >>> stripped_inner_xml('''
      ... <div>
      ...    This is some <i><b>really</b>
      ... silly</i> text!</div>''')
      u'This is some <i><b>really</b> silly</i> text!'
    """
    et = etree.parse(io.StringIO(xml_string))
    strip_xml(et.getroot())
    return inner_xml(etree.tounicode(et))


def remove_blank_lines(string):
    new_lines = []
    for line in string.splitlines():
        if line.strip():
            new_lines.append(line)

    return '\n'.join(new_lines)


def unicode_cleaner(string):
    if isinstance(string, str):
        return string

    try:
        return string.decode('utf-8')
    except UnicodeError:
        try:
            return string.decode('latin-1')
        except UnicodeError:
            return string.decode('utf-8', 'ignore')


def escape(string):
    """
    Escape a string into something safe to insert into HTML.
    """
    # Simplest escaping possible, kinda borrowed from jinja2.
    return (
        str(string)
        .replace('&', '&amp;')
        .replace('>', '&gt;')
        .replace('<', '&lt;')
        .replace("'", '&#39;')
        .replace('"', '&#34;'))


def locale_dict_fetch_with_fallbacks(data_dict, locale):
    """
    Take a dictionary with various locales as keys and translations as
    values and a locale, and try to find a value that matches with
    good fallbacks.
    """
    # try returning the locale as-is
    if locale in data_dict:
        return data_dict[locale]

    # nope?  try just returning the language...
    if '-' in locale:
        language, country = locale.split('-', 1)
        if language in data_dict:
            return data_dict[language]

    # still nope?  okay, try returning 'en', our default...
    if 'en' in data_dict:
        return data_dict['en']

    # still no??  last attempt!
    return data_dict[None]


###
## ISO 3166 -- country names to country code utilities
###

CODE_COUNTRY_LIST = sorted([
    (unicode_cleaner(code), unicode_cleaner(country))
    for code, country in csv.reader(
            open(pkg_resources.resource_filename('cc.license', 'iso3166.csv'),
                 encoding='utf-8'))],
    key=lambda country: country[1])
CODE_COUNTRY_MAP = dict(CODE_COUNTRY_LIST)
