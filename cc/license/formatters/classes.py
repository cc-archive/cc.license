
import os
from cc.license.lib.interfaces import ILicenseFormatter
import zope.interface
from genshi.template import TemplateLoader

class HTMLFormatter(object):
    zope.interface.implements(ILicenseFormatter)

    def __init__(self):
        self.loader = TemplateLoader(
                          os.path.join(os.path.dirname(__file__),'templates'),
                          auto_reload=False)
        self.tmpl = self.loader.load('html_rdfa.xml')

    @property
    def id(self):
        return "HTML + RDFa formatter"

    def format(self, license, work_graph=None, locale='en'):
        """Return an HTML + RDFa string serialization for the license,
            optionally incorporating the work metadata and locale."""
        stream = self.tmpl.generate(license=license, locale=locale)
        return stream.render('xhtml')
