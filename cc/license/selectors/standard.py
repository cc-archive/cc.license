import re
import zope.interface
import glob
import os
import cc.license
import RDF
from cc.license.interfaces import ILicenseSelector, ILicense
from cc.license.rdf_helper import query_to_single_value, NS_DC, NS_DCQ, NS_CC
import urlparse

## FIXME: One day make this not copy-pasta from sampling

class StandardLicense(object):
    zope.interface.implements(ILicense)
    def __init__(self, model, uri):
        assert ('by' in uri) or \
               ('nc' in uri) or \
               ('nd' in uri) or \
               ('sa' in uri) # I guess it should be a real license
        self.license_class = 'standard'

        # Assert that the model knows something about this URI
        # every CC license has a creator of http://creativecommons.org/
        assert (query_to_single_value(model,
                RDF.Uri(uri), RDF.Uri(NS_DC + 'creator'), None) \
                == 'http://creativecommons.org')

        self.version = query_to_single_value(model,
            RDF.Uri(uri),
            RDF.Uri(NS_DCQ + 'hasVersion'),
            None)
        self.jurisdiction = query_to_single_value(model,
            RDF.Uri(uri), RDF.Uri(NS_CC + 'jurisdiction'), None,
            'Your mother has no jurisdiction')
        self.uri = uri
        self.current_version = 'Your mom'  # FIXME: This should be calculated
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
        self._names = cc.license.rdf_helper.query_to_language_value_dict(model,
             RDF.Uri(self.uri),
             RDF.Uri('http://purl.org/dc/elements/1.1/title'),
             None)
    def name(self, language = 'en'):
        return self._names[language]

def relevant_rdf():
    ret = set()
    ret.update(glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH , '*by*.rdf')))
    ret.update(glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH , '*nc*.rdf')))
    ret.update(glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH , '*nd*.rdf')))
    ret.update(glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH , '*sa*.rdf')))
    return ret

class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = "Selector for sampling licenses"
    def __init__(self):
        files = relevant_rdf()
        self.model = cc.license.rdf_helper.init_model(*files)
        self.jurisdictions = None # FIXME
        self.versions = None # FIXME
    def by_uri(self, uri):
        # Check that the model knows about this license (e.g., it has a creator)
        try:
            assert (query_to_single_value(self.model,
                RDF.Uri(uri), RDF.Uri(NS_DC + 'creator'), None) \
                == 'http://creativecommons.org')
        except cc.license.rdf_helper.NoValuesFoundException:
            return None
        return StandardLicense(self.model, uri)
    def by_code(self, license_code, jurisdiction = None, version = None):
        base = 'http://creativecommons.org/licenses/'
        base = urlparse.urljoin(base, license_code + '/')
        if not version:
            version = '1.0' # FIXME: Should be latest_version
        base = urlparse.urljoin(base, version + '/')
        if jurisdiction:
            base = urlparse.urljoin(base, jurisdiction + '/')
        return self.by_uri(base)
    def by_answers(self, answers_dict):
        raise NotImplementedException
    def questions(self):
        raise NotImplementedException
