from cc.license.interfaces import ILicenseSelector
import zope.interface



class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = "Selector for public domain 'license'"
    def by_code(self, license_code, jurisdiction = None):
        pass
