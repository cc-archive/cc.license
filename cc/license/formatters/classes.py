"""
Formatters take a License instance and a dictionary of work metadata about
the licensed work. The keys of this work_dict are as follows:

 - format (Audio:Sound, Video:MovingImage, Image:StillImage,
           Text:Text, Interactive:InteractiveResource)
          Either this mapping above or the actual dctype
 - worktitle
 - attribution_name
 - attribution_url
 - source_work
 - more_permissions_url
"""
from future import standard_library
standard_library.install_aliases()
from builtins import object

from urllib.parse import urlparse

from cc.license import util
from cc.i18n.gettext_i18n import ugettext_for_locale
from cc.i18n.gettext_i18n import fake_ugettext as _
from cc.i18n.util import locale_to_lower_lower
from cc.i18n import mappers

import jinja2


TEMPLATE_LOADER = jinja2.PackageLoader('cc.license.formatters', 'templates')
TEMPLATE_ENV = jinja2.Environment(
    loader=TEMPLATE_LOADER, autoescape=False,
    extensions=['jinja2.ext.i18n'])


### --------------------------
### HTMLFormatter support functions
### --------------------------

IMAGE_HEADER_TEMPLATE = (
    '<a rel="license" href="%(license_url)s">'
    '<img alt="%(util.Creative_Commons_License)s" style="border-width:0"'
    ' src="%(license_logo)s" /></a><br />')


def get_dctype_url(dctype):
    return "http://purl.org/dc/dcmitype/%s" % dctype


WORK_TYPE_TEMPLATE = (
    '<span xmlns:dct="http://purl.org/dc/terms/"'
    ' href="%(dctype_url)s"'
    ' rel="dct:type">%(work)s</span>')

def process_work_type(gettext, dctype):
    work_word = gettext('work')
    if dctype:
        return WORK_TYPE_TEMPLATE % (
            {'dctype_url': get_dctype_url(dctype),
             'work': util.escape(work_word)})
    else:
        return util.escape(work_word)


DCTYPE_WORK_TITLE_TEMPLATE = (
    '<span xmlns:dct="http://purl.org/dc/terms/"'
    ' href="%(dctype_url)s"'
    ' property="dct:title"'
    ' rel="dct:type">%(worktitle)s</span>')
NO_DCTYPE_WORK_TITLE_TEMPLATE = (
    '<span xmlns:dct="http://purl.org/dc/terms/"'
    ' property="dct:title">%(worktitle)s</span>')

def process_work_title(dctype, worktitle):
    if dctype:
        return DCTYPE_WORK_TITLE_TEMPLATE % {
            'dctype_url': get_dctype_url(dctype),
            'worktitle': util.escape(worktitle)}
    else:
        return NO_DCTYPE_WORK_TITLE_TEMPLATE % {
            'worktitle': util.escape(worktitle)}


WORK_AUTHOR_TEMPLATE = (
    '<a xmlns:cc="http://creativecommons.org/ns#"'
    ' href="%(attribution_url)s" property="cc:attributionName"'
    ' rel="cc:attributionURL">%(attribution_name)s</a>')
WORK_AUTHOR_TEMPLATE_NO_URL = (
    '<span xmlns:cc="http://creativecommons.org/ns#"'
    ' property="cc:attributionName">%(attribution_name)s</span>')

def process_work_author(attribution_url, attribution_name):
    if attribution_url:
        return WORK_AUTHOR_TEMPLATE % {
            'attribution_name': util.escape(
                attribution_name or attribution_url),
            'attribution_url': util.escape(attribution_url)}
    else:
        return WORK_AUTHOR_TEMPLATE_NO_URL % {
            'attribution_name': util.escape(attribution_name)}


SOURCE_LINK_TEMPLATE = (
    '<a xmlns:dct="http://purl.org/dc/terms/"'
    ' href="%(source_work)s" rel="dct:source">%(source_domain)s</a>')

MORE_PERMS_LINK_TEMPATE = (
    '<a xmlns:cc="http://creativecommons.org/ns#"'
    ' href="%(more_permissions_url)s"'
    ' rel="cc:morePermissions">%(more_permissions_url)s</a>')


def _translate_dctype(format):
    # NOTE:
    #
    # So it's not clear if this function is needed or not.  Do we need
    # to support the Audio:Sound style mapping?  The current API and
    # Engine don't require it, but maybe an older version did.  Since
    # we're not sure we're keeping it here as legacy. :\
    try:
        return {
                 None : None,
                 'audio' : 'Sound',
                 'video' : 'MovingImage',
                 'image' : 'StillImage',
                 'text' : 'Text',
                 'interactive' : 'InteractiveResource',

                 # Original DCTYPES
                 # XXX: This is silly, but then again maybe this whole
                 #   function is silly.  Regardless, we already get the
                 #   format type from cc.engine in the correct form; no need
                 #   to translate.
                 'sound': 'Sound',
                 'movingimage': 'MovingImage',
                 'stillimage': 'StillImage',
                 'text': 'Text',
                 'interactiveresource': 'InteractiveResource',
                 'dataset': 'Dataset',
               }[format]
    except KeyError: # if we dont understand it, pretend its not there
        return None

### END HTMLFormatter support functions

class HTMLFormatter(object):

    def __repr__(self):
        return "<LicenseFormatter object '%s'>" % self.id

    def __str__(self):
        return '(%s)' % self.title

    @property
    def id(self):
        return 'html+rdfa'

    @property
    def title(self):
        return "HTML + RDFa formatter"

    def format(self, license, work_dict=None, locale='en'):
        """Return an HTML + RDFa string serialization for the license,
            optionally incorporating the work metadata and locale."""
        gettext = ugettext_for_locale(locale)

        work_dict = work_dict or {}

        image_header = IMAGE_HEADER_TEMPLATE % {
            'license_url': license.uri,
            'util.Creative_Commons_License': util.escape(
                gettext(u'Creative Commons License')),
            'license_logo': license.logo}

        dctype = None
        if work_dict.get('format'):
            dctype = _translate_dctype(work_dict['format'].lower())

        body_vars = {
            'license_url': license.uri,
            'license_name': util.escape(
                license.title(locale_to_lower_lower(locale)))}

        if ((work_dict.get('attribution_url')
             or work_dict.get('attribution_name'))
                and work_dict.get('worktitle')):
            body_template = gettext(
                    u'%(work_title)s by %(work_author)s is licensed under a '
                    u'<a rel="license" href="%(license_url)s">Creative Commons '
                    u'%(license_name)s License</a>.')
            body_vars.update(
                {'work_title': process_work_title(
                        dctype, work_dict['worktitle']),
                 'work_author': process_work_author(
                        work_dict.get('attribution_url'),
                        work_dict.get('attribution_name'))})
                 
        elif work_dict.get('attribution_url') \
                or work_dict.get('attribution_name'):
            body_template = gettext(
                    u'This %(work_type)s by %(work_author)s is licensed under '
                    u'a <a rel="license" href="%(license_url)s">Creative '
                    u'Commons %(license_name)s License</a>.')
            body_vars.update(
                {'work_type': process_work_type(gettext, dctype),
                 'work_author': process_work_author(
                        work_dict.get('attribution_url'),
                        work_dict.get('attribution_name'))})

        elif work_dict.get('worktitle'):
            body_template = gettext(
                    u'%(work_title)s is licensed under a '
                    u'<a rel="license" href="%(license_url)s">Creative Commons '
                    u'%(license_name)s License</a>.')
            body_vars.update(
                {'work_title': process_work_title(
                        dctype, work_dict['worktitle'])})

        else:
            body_template = gettext(
                    u'This %(work_type)s is licensed under a '
                    u'<a rel="license" href="%(license_url)s">Creative Commons '
                    u'%(license_name)s License</a>.')
            body_vars.update(
                {'work_type': process_work_type(gettext, dctype)})

        message = image_header + body_template % body_vars

        if work_dict.get('source_work'):
            source_work_template = gettext(
                u'Based on a work at %(source_link)s.')
            source_domain = urlparse(work_dict['source_work'])[1]
            if not source_domain.strip():
                source_domain = work_dict['source_work']
            source_work = source_work_template % {
                'source_link': SOURCE_LINK_TEMPLATE % {
                    'source_work': util.escape(work_dict['source_work']),
                    'source_domain': util.escape(source_domain)}}
            message = message + "<br />" + source_work

        if work_dict.get('more_permissions_url'):
            more_perms_template = gettext(
                    u'Permissions beyond the scope of this license may be '
                    u'available at %(more_perms_link)s.')
            more_perms = more_perms_template % {
                'more_perms_link': MORE_PERMS_LINK_TEMPATE % {
                    'more_permissions_url': util.escape(
                        work_dict['more_permissions_url'])}}
            message = message + "<br />" + more_perms

        return message


class CC0HTMLFormatter(HTMLFormatter):
    def __repr__(self):
        return "<CC0LicenseFormatter object '%s'>" % self.id

    def format(self, license, work_dict=None, locale='en'):
        gettext = ugettext_for_locale(locale)

        work_dict = work_dict or {}

        work_title = work_dict.get('work_title', False)
        actor_href = work_dict.get('actor_href', '').strip()
        actor = work_dict.get('name', '').strip()

        template = TEMPLATE_ENV.get_template('cc0.html')

        work_jurisdiction = work_dict.get('work_jurisdiction')
        country_name = None
        if work_jurisdiction not in ('', '-', None, False):
            if work_jurisdiction.lower() in mappers.COUNTRY_MAP:
                country_name = gettext(
                    mappers.COUNTRY_MAP[work_jurisdiction.lower()])
            # Crappy fallback to this CSV.  We should homogenize these
            # things...
            elif work_jurisdiction.upper() in util.CODE_COUNTRY_MAP:
                country_name = gettext(
                    util.CODE_COUNTRY_MAP[work_jurisdiction.upper()])

        rendered_template = template.render(
            {"gettext": gettext,
             "license": license,
             "actor": actor,
             "actor_href": actor_href,
             "work_jurisdiction": work_jurisdiction,
             "publisher": actor_href or "[_:publisher]",
             "country_name": country_name,
             "work_title": work_title,
             "form": work_dict})

        return util.remove_blank_lines(rendered_template)


class PublicDomainHTMLFormatter(HTMLFormatter):
    def __repr__(self):
        return "<PublicDomainLicenseFormatter object '%s'>" % self.id

    def format(self, license, work_dict=None, locale='en'):
        work_dict = work_dict or {}

        gettext = ugettext_for_locale(locale)

        dctype = None
        if work_dict.get('format'):
            dctype = _translate_dctype(work_dict['format'].lower())

        image_header = IMAGE_HEADER_TEMPLATE % {
            'license_url': license.uri,
            'util.Creative_Commons_License': util.escape(gettext(
                u'Creative Commons License')),
            'license_logo': license.logo}

        body_template = gettext(
            u'This %(work_type)s is in the '
            u'<a rel="license" href="http://creativecommons.org/licenses/publicdomain/">Public Domain</a>.')
        body_vars = {'work_type': process_work_type(gettext, dctype)}

        message = image_header + body_template % body_vars

        return message


### ----------------------------
### Public Domain Mark formatter
### ----------------------------

PDMARK_PLAIN = _(
    "This work is free of known copyright restrictions.")
    
PDMARK_WORKTITLE = _(
    "This work (%(work_title)s) is free of known copyright restrictions.")

PDMARK_AUTHOR = _(
    'This work '
    '(by %(author)s) '
    'is free of known copyright restrictions.')

PDMARK_CURATOR = _(
    'This work, '
    'identified by %(curator)s, '
    'is free of known copyright restrictions.')

PDMARK_WORKTITLE_AUTHOR = _(
    'This work (%(work_title)s, by %(author)s) '
    'is free of known copyright restrictions.')

PDMARK_WORKTITLE_CURATOR = _(
    'This work (%(work_title)s), '
    'identified by %(curator)s, '
    'is free of known copyright restrictions.')

PDMARK_WORKTITLE_AUTHOR_CURATOR = _(
    'This work (%(work_title)s, '
    'by %(author)s), identified by %(curator)s, '
    'is free of known copyright restrictions.')

PDMARK_AUTHOR_CURATOR = _(
    'This work '
    '(by %(author)s), identified by %(curator)s, '
    'is free of known copyright restrictions.')


# The "links" html that are substituted into the wider templates
PDMARK_AUTHOR_LINK = (
    u'<a href="%(author_href)s" rel="dct:creator">'
    u'<span property="dct:title">%(author_title)s</span></a>')
PDMARK_AUTHOR_NOLINK = (
    u'<span resource="[_:creator]" rel="dct:creator">'
    u'<span property="dct:title">%(author_title)s</span></span>')
PDMARK_AUTHOR_ONLYLINK = (
    u'<a href="%(author_href)s" rel="dct:creator">'
    u'%(author_href)s</a>')

PDMARK_CURATOR_LINK = (
    u'<a href="%(curator_href)s" rel="dct:publisher">'
    u'<span property="dct:title">%(curator_title)s</span></a>')
PDMARK_CURATOR_NOLINK = (
    u'<span resource="[_:publisher]" rel="dct:publisher">'
    u'<span property="dct:title">%(curator_title)s</span></span>')
PDMARK_CURATOR_ONLYLINK = (
    u'<a href="%(curator_href)s" rel="dct:publisher">'
    u'%(curator_href)s</a>')


PDMARK_LOGO_HTML = """<a rel="license" href="http://creativecommons.org/publicdomain/mark/1.0/">
<img src="http://i.creativecommons.org/p/mark/1.0/88x31.png"
     style="border-style: none;" alt="Public Domain Mark" />
</a>"""

CC0_LOGO_HTML = """<a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/">
<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"
     style="border-style: none;" alt="CC0" />
</a>"""

class PDMarkHTMLFormatter(HTMLFormatter):
    """
    Formatter for the Public Domain Mark
    """
    def __repr__(self):
        return "<PDMarkLicenseFormatter object '%s'>" % self.id

    def format(self, license, work_dict=None, locale='en'):
        """
        Return an HTML + RDFa string of text for the license.

        work_dict takes the following keys:
         - work_title: Name of the work
         - author_title: Original author of the work
         - author_href: Link to the original author of the work
         - curator_title: The person who identified this work
         - curator_href: Link to the person who identified this work
         - waive_cc0: Whether the author has also waived their rights
           under CC0 (boolean)
        """
        gettext = ugettext_for_locale(locale)

        # Property gathering
        # ------------------
        work_dict = work_dict or {}

        work_title = work_dict.get('work_title', False)

        author_title = work_dict.get('author_title', '').strip()
        author_href = work_dict.get('author_href', '').strip()

        curator_title = work_dict.get('curator_title', '').strip()
        curator_href = work_dict.get('curator_href', '').strip()

        waive_cc0 = work_dict.get('waive_cc0', False)

        # Find the "body" template
        # ------------------------

        has_author = bool(author_title or author_href)
        has_curator = bool(curator_title or curator_href)

        # All (work_title and author and curator)
        if work_title and has_author and has_curator:
            body_msg = PDMARK_WORKTITLE_AUTHOR_CURATOR
        # Only work_title
        elif work_title and not has_author and not has_curator:
            body_msg = PDMARK_WORKTITLE
        # Only author
        elif has_author and not work_title and not has_curator:
            body_msg = PDMARK_AUTHOR
        # Only curator
        elif has_curator and not work_title and not has_author:
            body_msg = PDMARK_CURATOR
        # work_title and author
        elif work_title and has_author and not has_curator:
            body_msg = PDMARK_WORKTITLE_AUTHOR
        # work_title and curator
        elif work_title and has_curator and not has_author:
            body_msg = PDMARK_WORKTITLE_CURATOR
        # author and curator
        elif has_author and has_curator and not work_title:
            body_msg = PDMARK_AUTHOR_CURATOR
        # plain
        else:
            body_msg = PDMARK_PLAIN

        # Translate the body
        # ------------------
        mapping = {}

        if work_title:
            mapping['work_title'] = u'<span property="dct:title">%s</span>' % (
                util.escape(work_title))

        if has_author:
            if author_title and author_href:
                mapping['author'] = PDMARK_AUTHOR_LINK % (
                    {'author_title': util.escape(author_title),
                     'author_href': util.escape(author_href)})
            elif author_title and not author_href:
                mapping['author'] = PDMARK_AUTHOR_NOLINK % (
                    {'author_title': util.escape(author_title)})
            elif author_href and not author_title:
                mapping['author'] = PDMARK_AUTHOR_ONLYLINK % (
                    {'author_href': util.escape(author_href)})
                
        if has_curator:
            if curator_title and curator_href:
                mapping['curator'] = PDMARK_CURATOR_LINK % (
                    {'curator_title': util.escape(curator_title),
                     'curator_href': util.escape(curator_href)})
            elif curator_title and not curator_href:
                mapping['curator'] = PDMARK_CURATOR_NOLINK % (
                    {'curator_title': util.escape(curator_title)})
            elif curator_href and not curator_title:
                mapping['curator'] = PDMARK_CURATOR_ONLYLINK % (
                    {'curator_href': util.escape(curator_href)})

        body = gettext(body_msg) % mapping

        # Add the header and footers
        # --------------------------
        output_sections = []

        # XXX: Norms guidelines may affect opening <p>?
        if work_title or has_author or has_curator:
            output_sections.append(
                u'<p xmlns:dct="http://purl.org/dc/terms/">')
        else:
            output_sections.append(u'<p>')

        # Add logos
        output_sections.append(PDMARK_LOGO_HTML)
        if waive_cc0:
            output_sections.append(CC0_LOGO_HTML)

        output_sections.append(u'<br />')

        # Add body
        output_sections.append(body)

        # Add footer
        output_sections.append(u'</p>')

        return u'\n'.join(output_sections)
