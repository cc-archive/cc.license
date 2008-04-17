from cc.license.interfaces import ILicenseFormatter
import zope.interface

class Formatter(object):
    zope.interface.implements(ILicenseFormatter)
    id = "HTML + RDFa formatter"
    def format(self, license, work_dict = {}, locale = 'en'):
        """Return a string serialization for the license, optionally 
        incorporating the work metadata and locale."""
        raise NotImplementedYet # !

