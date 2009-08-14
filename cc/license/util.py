from lxml import etree
import StringIO


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
      >>> etree.tostring(cleaned_root_mess)
      '<help>How did<person>I</person>get to be so<cleanliness xmlns:clean="http://example.org/howclean/#" clean:cleanliness="filthy">messy</cleanliness>?</help>'

    Note that strip_xml operates on the mutability of the argument
    `element`, so the object returned is the same object that's passed
    in.

      >>> cleaned_root_mess is etree_mess.getroot()
      True
    """
    def _recursive_strip(elt):
        elt.text = strip_text(elt.text)
        elt.tail = strip_text(elt.tail)

        for child in elt:
            _recursive_strip(child)

    _recursive_strip(element)
    return element


def inner_xml(elt):
    """
    Get the inner xml of an element.

      >>> html_etree = etree.parse(
      ...   StringIO.StringIO(
      ...     '<div>This is some <i><b>really</b> silly</i> text!</div>'))
      >>> inner_xml(html_etree.getroot())
      u'This is some <i><b>really</b> silly</i> text!'
    """
    return (unicode(elt.text) or u'') \
        + u''.join(etree.tostring(child) for child in elt)


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
      u'This is some <i><b>really</b> silly</i>text!'
    """
    et = etree.parse(StringIO.StringIO(xml_string))
    strip_xml(et.getroot())
    return inner_xml(et.getroot())
