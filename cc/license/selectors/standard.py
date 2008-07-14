import re
import zope.interface
import glob
import os
import RDF
import cc.license
from cc.license.lib.interfaces import ILicenseSelector, ILicense
from cc.license.lib.rdf_helper import query_to_single_value, NS_DC, \
                                      NS_DCQ, NS_CC
from cc.license.lib.exceptions import NoValuesFoundError
from cc.license.lib import rdf_helper

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

        self.deprecated_date = query_to_single_value(model,
            RDF.Uri(uri),
            RDF.Uri(NS_CC + 'deprecatedOn'),
            None,
            default = None)
        if self.deprecated_date is None:
            self.deprecated = False
        else:
            self.deprecated = True
        replaced_by = query_to_single_value(model,
            RDF.Uri(uri),
            RDF.Uri(NS_DCQ + 'isReplacedBy'),
            None, default = None)
        if replaced_by:
            selector = cc.license.selectors.choose('standard')
            self.superseded = selector.by_uri(replaced_by)
        else:
            self.superseded = None

        self._calculate_current_version()

        self.license_code = re.match(r'http://creativecommons.org/licenses/([^/]+)/.*',
                uri).group(1) # FIXME: Hilariously lame regex until ML and NY and AL talk
        self.libre = False # FIXME: Pull out of freedomdefined.rdf
        self._names = rdf_helper.query_to_language_value_dict(model,
             RDF.Uri(self.uri),
             RDF.Uri('http://purl.org/dc/elements/1.1/title'),
             None)
    def _calculate_current_version(self):
        best_version_found = self

        # FIXME: use a real license version comparator
        # Something aware of version numbers, like 1.5b2 maybe
        ## Is there some Pythonland standard tool for this, like for Python itself?
        while best_version_found.superseded:
            best_version_found = best_version_found.superseded
        self.current_version = best_version_found

    def name(self, language = 'en'):
        return self._names[language]

def relevant_rdf():
    ret = set()
    ret.update(glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH , '*by*.rdf')))
    ret.update(glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH , '*nc*.rdf')))
    ret.update(glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH , '*nd*.rdf')))
    ret.update([ l for l in glob.glob(os.path.join(rdf_helper.LIC_RDF_PATH,
                                      '*sa*.rdf'))
                       if l.find('sampling') != -1 ])
                       # hack to remove sampling licenses
    return ret

# TODO: pull id and title from license.rdf
class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = 'standard'
    title = 'Creative Commons'

    def __init__(self):
        self._licenses = {}
        files = relevant_rdf()
        self.model = rdf_helper.init_model(*files)
        self.jurisdictions = None # FIXME
        self.versions = None # FIXME

    def _by_uri(self, uri):
        # Check that the model knows about this license (e.g., it has a creator)
        try:
            assert (query_to_single_value(self.model,
                RDF.Uri(uri), RDF.Uri(NS_DC + 'creator'), None) \
                == 'http://creativecommons.org')
        except NoValuesFoundError:
            return None
        return StandardLicense(self.model, uri)

    def by_uri(self, uri):
        if uri not in self._licenses:
            self._licenses[uri] = self._by_uri(uri)
        return self._licenses[uri]

    def by_code(self, license_code, jurisdiction=None, version=None):
        uri = cc.license.lib.dict2uri(dict(jurisdiction=jurisdiction,
                                           version=version,
                                           code=license_code))
        return self.by_uri(uri)

    def by_answers(self, answers_dict):
        raise NotImplementedError

    def questions(self):
        raise NotImplementedError
