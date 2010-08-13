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

import cgi
import string
from urlparse import urlparse

import zope.interface

from cc.license._lib.interfaces import ILicenseFormatter
from cc.license import util
from cc.i18n.gettext_i18n import ugettext_for_locale

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
    '<span xmlns:dc="http://purl.org/dc/elements/1.1/"'
    ' href="%(dctype_url)s"'
    ' rel="dc:type">%(work)s</span>')

def process_work_type(gettext, dctype):
    work_word = gettext('util.work')
    if dctype:
        return WORK_TYPE_TEMPLATE % (
            {'dctype_url': get_dctype_url(dctype),
             'work': util.escape(work_word)})
    else:
        return util.escape(work_word)


DCTYPE_WORK_TITLE_TEMPLATE = (
    '<span xmlns:dc="http://purl.org/dc/elements/1.1/"'
    ' href="%(dctype_url)s"'
    ' property="dc:title"'
    ' rel="dc:type">%(worktitle)s</span>')
NO_DCTYPE_WORK_TITLE_TEMPLATE = (
    '<span xmlns:dc="http://purl.org/dc/elements/1.1/"'
    ' property="dc:title">%(worktitle)s</span>')

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
    '<a xmlns:dc="http://purl.org/dc/elements/1.1/"'
    ' href="%(source_work)s" rel="dc:source">%(source_domain)s</a>')

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
               }[format]
    except KeyError: # if we dont understand it, pretend its not there
        return None

### END HTMLFormatter support functions

class HTMLFormatter(object):
    zope.interface.implements(ILicenseFormatter)

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
            'util.Creative_Commons_License': util.escape(gettext(
                'util.Creative_Commons_License')),
            'license_logo': license.logo}

        dctype = None
        if work_dict.get('format'):
            dctype = _translate_dctype(work_dict['format'].lower())

        body_vars = {
            'license_url': license.uri,
            'license_name': util.escape(license.title(locale))}

        if ((work_dict.get('attribution_url')
             or work_dict.get('attribution_name'))
                and work_dict.get('worktitle')):
            body_template = string.Template(
                gettext('license.rdfa_licensed'))
            body_vars.update(
                {'work_title': process_work_title(
                        dctype, work_dict['worktitle']),
                 'work_author': process_work_author(
                        work_dict.get('attribution_url'),
                        work_dict.get('attribution_name'))})
                 
        elif work_dict.get('attribution_url') \
                or work_dict.get('attribution_name'):
            body_template = string.Template(
                gettext('license.rdfa_licensed_no_title'))
            body_vars.update(
                {'work_type': process_work_type(gettext, dctype),
                 'work_author': process_work_author(
                        work_dict.get('attribution_url'),
                        work_dict.get('attribution_name'))})

        elif work_dict.get('worktitle'):
            body_template = string.Template(
                gettext('license.rdfa_licensed_no_attrib'))
            body_vars.update(
                {'work_title': process_work_title(
                        dctype, work_dict['worktitle'])})

        else:
            work_type = process_work_type(gettext, dctype)
            body_template = string.Template(
                gettext('license.work_type_licensed'))
            body_vars.update(
                {'work_type': process_work_type(gettext, dctype)})

        message = image_header + body_template.substitute(body_vars)

        if work_dict.get('source_work'):
            source_work_template = string.Template(
                gettext('license.work_based_on'))
            source_domain = urlparse(work_dict['source_work'])[1]
            if not source_domain.strip():
                source_domain = work_dict['source_work']
            source_work = source_work_template.substitute(
                {'source_link': SOURCE_LINK_TEMPLATE % {
                        'source_work': util.escape(work_dict['source_work']),
                        'source_domain': util.escape(source_domain)}})
            message = message + "<br />" + source_work

        if work_dict.get('more_permissions_url'):
            more_perms_template = string.Template(
                gettext('license.more_perms_available'))
            more_perms = more_perms_template.substitute(
                {'more_perms_link': MORE_PERMS_LINK_TEMPATE % {
                        'more_permissions_url': util.escape(
                            work_dict['more_permissions_url'])}})
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
            country_name = gettext(util.CODE_COUNTRY_MAP[work_jurisdiction])

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
                'util.Creative_Commons_License')),
            'license_logo': license.logo}

        body_template = string.Template(
            gettext('license.work_type_dedicated'))
        body_vars = {'work_type': process_work_type(gettext, dctype)}

        message = image_header + body_template.substitute(body_vars)

        return message


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
         - work_href: Link to this work
         - creator: Original author of the work
         - creator_href: Link to the original author of the work
         - curator: The person who identified this work
         - curator_href: Link to the person who identified this work
         - norms_href: Link to norms for this work
         - waive_cc0: Whether the author has also waived their rights
           under CC0
        """
        work_dict = work_dict or {}

        gettext = ugettext_for_locale(locale)

        work_title = work_dict.get('work_title', False)
        work_href = work_dict.get('work_href', False)

        creator = work_dict.get('creator', '').strip()
        creator_href = work_dict.get('creator_href', '').strip()

        curator = work_dict.get('curator', '').strip()
        curator_href = work_dict.get('curator_href', '').strip()

        norms_href = work_dict.get('norms_href', '').strip()

        waive_cc0 = work_dict.get('waive_cc0', False)

        template = TEMPLATE_ENV.get_template('pdmark.html')

        rendered_template = template.render(
            {"gettext": gettext,
             "work_title": work_title,
             "work_href": work_href,
             "creator": creator,
             "creator_href": creator_href,
             "curator": curator,
             "curator_href": curator_href,
             "norms_href": norms_href,
             "waive_cc0": waive_cc0,
             "form": work_dict})

        return util.remove_blank_lines(rendered_template)
