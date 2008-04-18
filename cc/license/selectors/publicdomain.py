import RDF
from cc.license.interfaces import ILicenseSelector, ILicense
import cc.license
import cc.license.rdf_helper

import zope.interface
import glob
import os

class PdLicense(object):
    zope.interface.implements(ILicense)
    def __init__(self, model, uri):
        assert uri == 'http://creativecommons.org/licenses/publicdomain/'
        self.license_class = 'publicdomain' # LAME, should pull from RDF
        self.version = 'Your mom' # Is there a version for the PD deed?
        self.jurisdiction = 'Your mom' # Is there a juri?  US?  (Not in the RDF)
        self.uri = uri
        self.current_version = 'Your mom' # Is there versioning for PD?
        self.deprecated = False # I think
        self.superseded = False # I think
        self.license_code = 'publicdomain' # Based on assertion at top of init
        self.libre = True # Sure, I think?  Not in the RDF.
        self._names = cc.license.rdf_helper.query_to_language_value_dict(model,
             RDF.Uri(self.uri),
             RDF.Uri('http://purl.org/dc/elements/1.1/title'),
             None)
    def name(self, language = 'en'):
        return self._names[language]
        

class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = "Selector for public domain 'license'"
    def __init__(self):
        files = glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH ,'*publicdomain*'))
        self.model = cc.license.rdf_helper.init_model(*files)

    def by_uri(self, uri):
        value = cc.license.rdf_helper(self.model,
                                      RDF.Uri(uri),
                                      RDF.Uri(cc.license.rdf_helper.NS_CC + 'legalcode'),
                                      None)
        if value:
            return value
        raise "your mom"
    
    def by_code(self, code):
        if code == 'publicdomain':
            return self.by_uri('http://creativecommons.org/licenses/publicdomain/')
    
    def by_uri(self, uri):
        return PdLicense(self.model, uri)
