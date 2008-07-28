from cc.license.lib.interfaces import ILicenseFormatter
import zope.interface

class HTMLFormatter(object):
    zope.interface.implements(ILicenseFormatter)

    id = "HTML + RDFa formatter"

    def format(self, license, work_graph, locale='en'):
        """Return an HTML + RDFa string serialization for the license,
            optionally incorporating the work metadata and locale."""
        raise NotImplementedYet # !
