"""
Formatters take a License instance and a dictionary of work metadata about
the licensed work. The keys of this work_dict are as follows:

 - format
   The format of the work, values can be one of:
     - Audio (Sound)
     - Video (MovingImage)
     - Image (StillImage)
     - Text (Text)
     - Interactive (InteractiveResource)

 - worktitle
   Title of work

 - attribution_name
   Attribute work to name

 - attribution_url
   Attribute work to URL

 - source_work
   Source work URL

 - more_permissions_url
   More permissions URL
"""

import os
from cc.license._lib.interfaces import ILicenseFormatter
from cc.license._lib.exceptions import CCLicenseError
import zope.interface
from genshi.template import TemplateLoader
from filters import Source, Permissions

# template loader, which is reused in a few places
LOADER = TemplateLoader(
             os.path.join(os.path.dirname(__file__), 'templates'),
             auto_reload=False)

class HTMLFormatter(object):
    zope.interface.implements(ILicenseFormatter)

    def __init__(self):
        pass

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

    def format(self, license, work_dict={}, locale='en'):
        """Return an HTML + RDFa string serialization for the license,
            optionally incorporating the work metadata and locale."""
        w = work_dict # alias work_dict for brevity

        # FOUR CASES!
        case = 0
        if w.has_key('format') or w.has_key('worktitle'):
            case += 1
        if w.has_key('attribution_name') or w.has_key('attribution_url'):
            case += 2

        # switch statement

        # fill out work_dict with defaults
        for attr in ('more_permissions_url', 'worktitle', 'attribution_name',
                     'attribution_url', 'source_work', 'format'):
            if not w.has_key(attr):
                w[attr] = None

        format = None
        dctype = None
        if w['format'] is not None:
            chosen_tmpl = 'work.xml'
            format = work_dict['format'].lower()
            try:
                dctype_chooser = {
                                  None : None,
                                  'audio' : 'Sound',
                                  'video' : 'MovingImage',
                                  'image' : 'StillImage',
                                  'text' : 'Text',
                                  'interactive' : 'InteractiveResource',
                                 }[format]
            except KeyError:
                chosen_tmpl = 'work.xml'
        else:
            chosen_tmpl = 'default.xml'
        self.tmpl = LOADER.load(chosen_tmpl)
        stream = self.tmpl.generate(license=license, 
                                    locale=locale,
                                    format=format,
                                    dctype=dctype)
        stream = stream | Source(work_dict) | Permissions(work_dict)
        return stream.render('xhtml')
