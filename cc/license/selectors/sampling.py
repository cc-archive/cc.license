import re
import zope.interface
import glob
import os
import RDF
import cc.license
from cc.license.lib.classes import License
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib import rdf_helper
import urlparse

# TODO: pull id and title from license.rdf
class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = 'recombo'
    title = 'Sampling'

    def __init__(self):
        files = glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH ,'*sampling*'))
        self.model = rdf_helper.init_model(*files)
        self.jurisdictions = None # FIXME
        self.versions = None # FIXME

    def by_uri(self, uri):
        return License(self.model, uri)

    def by_code(self, license_code, jurisdiction=None, version=None):
        uri = cc.license.lib.dict2uri(dict(jurisdiction=jurisdiction,
                                           version=version,
                                           code=license_code))
        return self.by_uri(uri)

    def by_answers(self, answers_dict):
        raise NotImplementedError

    def questions(self):
        raise NotImplementedError
            
