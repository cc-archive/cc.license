"""
Formatters take a License instance and a dictionary of work metadata about
the licensed work. The keys of this work_dict are as follows:

 - format (Audio:Sound, Video:MovingImage, Image:StillImage,
           Text:Text, Interactive:InteractiveResource)
 - worktitle
 - attribution_name
 - attribution_url
 - source_work
 - more_permissions_url
"""

import zope.interface

from cc.license._lib.interfaces import ILicenseFormatter
from cc.license import util
from cc.i18npkg.gettext_i18n import ugettext_for_locale

import jinja2

TEMPLATE_LOADER = jinja2.PackageLoader('cc.license.formatters', 'templates')
TEMPLATE_ENV = jinja2.Environment(
    loader=TEMPLATE_LOADER, autoescape=False,
    extensions=['jinja2.ext.i18n'])


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

    def _translate_dctype(self, format):
        try:
            return {
                     None : None,
                     'audio' : 'Sound',
                     'video' : 'MovingImage',
                     'image' : 'StillImage',
                     'text' : 'Text',
                     'interactive' : 'InteractiveResource',
                   }[format]
        except KeyError: # if we dont understand it, pretend its not there
            return None

    def format(self, license, work_dict=None, locale='en'):
        """Return an HTML + RDFa string serialization for the license,
            optionally incorporating the work metadata and locale."""
        gettext = ugettext_for_locale(locale)

        work_dict = work_dict or {}

        if ((work_dict.get('attribution_url')
             or work_dict.get('attribution_name'))
                and work_dict.get('worktitle')):
            template = TEMPLATE_ENV.get_template('attribution_worktitle.html')
        elif work_dict.get('attribution_url') \
                or work_dict.get('attribution_name'):
            template = TEMPLATE_ENV.get_template('attribution.html')
        elif work_dict.get('worktitle'):
            template = TEMPLATE_ENV.get_template('worktitle.html')
        else:
            template = TEMPLATE_ENV.get_template('default.html')

        dctype = None
        if work_dict.get('format'):
            dctype = self._translate_dctype(work_dict['format'].lower())

        rendered_template = template.render(
            {"gettext": gettext,
             "dctype": dctype,
             "dctype_url": "http://purl.org/dc/dcmitype/%s" % dctype,
             "this_license": license,
             "locale": util.locale_to_dash_style(locale),
             "worktitle": work_dict.get('worktitle'),
             "attribution_name": (work_dict.get('attribution_name')
                                  or work_dict.get('attribution_url')),
             "attribution_url": work_dict.get('attribution_url'),
             "source_work": work_dict.get('source_work'),
             "more_permissions_url": work_dict.get('more_permissions_url'),
             "test_false": False})
        return util.stripped_inner_xml(rendered_template)


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

