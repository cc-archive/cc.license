import RDF
from cc.license.interfaces import ILicenseSelector
import cc.license
import cc.license.rdf_helper

import zope.interface
import glob

class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = "Selector for public domain 'license'"
    def __init__(self):
        files = glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH ,'*publicdomain*'))
        self.model = cc.license.rdf_helper.init_model(files.pop())
        parser = RDF.Parser('raptor')
        for file in files: # for remaining files
            parser.parse_into_model(self.model, RDF.Uri(string='file:' + file))

    def by_uri(self, uri):
        value = cc.license.rdf_helper(self.model,
                                      RDF.Uri(uri),
                                      RDF.Uri(cc.license.rdf_helper.NS_CC + 'legalcode'),
                                      None)
        if value:
            return value
        raise "your mom"
        
