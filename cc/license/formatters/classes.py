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

import os
from cc.license._lib.interfaces import ILicenseFormatter
import zope.interface

from chameleon.zpt.template import PageTemplateFile

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates')
BASE_TEMPLATE = os.path.join(TEMPLATE_PATH, 'base.pt')
DEFAULT_HEADER_TEMPLATE = os.path.join(TEMPLATE_PATH, 'default_header.pt')
ATTRIBUTION_HEADER_TEMPLATE = os.path.join(TEMPLATE_PATH,
                                           'attribution_header.pt')
WORKTITLE_HEADER_TEMPLATE = os.path.join(TEMPLATE_PATH, 'worktitle_header.pt')

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
        
        work_dict = work_dict or {}

        main_text_type = 'default'
        if work_dict.get('attribution_url') \
                or work_dict.get('attribution_name'):
            main_text_type = 'attribution'
        elif work_dict.get('worktitle'):
            main_text_type = 'worktitle'

        dctype = None
        if work_dict.get('format'):
            dctype = self._translate_dctype(work_dict['format'].lower())

        base_template = PageTemplateFile(BASE_TEMPLATE)
        return base_template.render(
            main_text_type=main_text_type,
            dctype=dctype,
            this_license=license, locale=locale,
            worktitle=work_dict.get('worktitle'),
            default_header=PageTemplateFile(DEFAULT_HEADER_TEMPLATE),
            attribution_header=PageTemplateFile(ATTRIBUTION_HEADER_TEMPLATE),
            worktitle_header=PageTemplateFile(WORKTITLE_HEADER_TEMPLATE),
            attribution_name=(work_dict.get('attribution_name')
                              or work_dict.get('attribution_url')),
            attribution_url=(work_dict.get('attribution_url')
                             or work_dict.get('attribution_name')),
            source_work=work_dict.get('source_work'),
            more_permissions_url=work_dict.get('more_permissions_url'))
