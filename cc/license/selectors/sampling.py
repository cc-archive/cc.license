import re
import zope.interface
import glob
import os
import RDF
from cc.license.lib.interfaces import ILicenseSelector, ILicense
from cc.license.lib.rdf_helper import query_to_single_value, NS_DC, \
                                      NS_DCQ, NS_CC
from cc.license.lib import rdf_helper
import urlparse

# Note: this could be lazy, but then errors would be detected really late
#  - is that really what we want?
class SamplingLicense(object):
    zope.interface.implements(ILicense)
    def __init__(self, model, uri):
        assert '1.0' in uri # since version not in RDF
        assert 'sampling' in uri # we are a sampling license, right?

        self.license_class = 'recombo' # Is this right?
        self.version = query_to_single_value(model,
            RDF.Uri(uri),
            RDF.Uri(NS_DCQ + 'hasVersion'),
            None)
        self.jurisdiction = 'Your mom' # Unknown
        self.uri = uri
        self.current_version = 'Your mom' # FIXME: This should be calculated
                                         # and passed in by the Selector,
                                        # I guess?
        self.deprecated_date = query_to_single_value(model,
            RDF.Uri(uri),
            RDF.Uri(NS_CC + 'deprecatedOn'),
            None,
            default = None)
        if self.deprecated_date is None:
            self.deprecated = False
        else:
            self.deprecated = True
        self.superseded = False # FIXME: Should be passed in by the Selector
        self.license_code = re.match(r'http://creativecommons.org/licenses/([^/]+)/.*',
                uri).group(1) # FIXME: Hilariously lame regex
        self.libre = False # FIXME: Pull out of RDF?
        self._names = rdf_helper.query_to_language_value_dict(model,
             RDF.Uri(self.uri),
             RDF.Uri('http://purl.org/dc/elements/1.1/title'),
             None)
    def name(self, language = 'en'):
        return self._names[language]

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
        return SamplingLicense(self.model, uri)
    def by_code(self, license_code, jurisdiction = None, version = None):
        base = 'http://creativecommons.org/licenses/'
        base = urlparse.urljoin(base, license_code + '/')
        if not version:
            version = '1.0'
        base = urlparse.urljoin(base, version + '/')
        if jurisdiction:
            base = urlparse.urljoin(base, jurisdiction + '/')
        return self.by_uri(base)
    def by_answers(self, answers_dict):
        raise NotImplementedError
    def questions(self):
        raise NotImplementedError
            
