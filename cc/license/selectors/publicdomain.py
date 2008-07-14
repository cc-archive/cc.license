import RDF
from cc.license.lib.classes import License
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib import rdf_helper

import zope.interface
import glob
import os

# TODO: pull id and title from license.rdf
class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = 'publicdomain'
    title = 'Public Domain'
    def __init__(self):
        files = glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH ,'*publicdomain*'))
        self.model = rdf_helper.init_model(*files)

    def by_code(self, code):
        if code == 'publicdomain':
            return self.by_uri('http://creativecommons.org/licenses/publicdomain/')
    
    def by_uri(self, uri):
        return License(self.model, uri)
