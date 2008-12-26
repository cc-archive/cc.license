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
        # TODO: get rid of this one day
        for attr in ('more_permissions_url', 'worktitle', 'attribution_name',
                     'attribution_url', 'source_work', 'format'):
            if not w.has_key(attr):
                w[attr] = None

        chosen_tmpl = None
        format = None
        dctype = None
        kwargs = dict(w) # copy it over

        if w['format'] is not None:
            format = work_dict['format'].lower()
            chosen_tmpl = 'work_%s.xml' % format
            try:
                dctype = {
                          None : None,
                          'audio' : 'Sound',
                          'video' : 'MovingImage',
                          'image' : 'StillImage',
                          'text' : 'Text',
                          'interactive' : 'InteractiveResource',
                         }[format]
            except KeyError:
                chosen_tmpl = 'default.xml'

        if w['worktitle'] is not None:
            chosen_tmpl = 'worktitle.xml'

        if w['attribution_name'] is not None: # try it out
            chosen_tmpl = 'title_attribution.xml'

        if w['attribution_url'] is not None:
            chosen_tmpl = 'title_attribution.xml'

        # pack kwargs
        kwargs['license'] = license
        kwargs['locale'] = locale
        kwargs['dctype'] = dctype
        if w.has_key('worktitle'): # superfluous, for now
            kwargs['worktitle'] = w['worktitle']
        
        # default
        if chosen_tmpl is None:
            chosen_tmpl = 'default.xml'

        self.tmpl = LOADER.load(chosen_tmpl)
        stream = self.tmpl.generate(**kwargs)
        stream = stream | Source(work_dict) | Permissions(work_dict)
        return stream.render('xhtml')
