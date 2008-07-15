import re
import zope.interface
import glob
import os
import RDF
import cc.license
from cc.license.lib.classes import License
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib.rdf_helper import query_to_single_value, NS_DC
from cc.license.lib.exceptions import NoValuesFoundError
from cc.license.lib import rdf_helper

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
        self.jurisdictions = None # FIXME, what should it be??
        self.versions = None # FIXME, what should it be??

    def _by_uri(self, uri):
        # Check that the model knows about this license (e.g., it has a creator)
        try:
            assert (query_to_single_value(self.model,
                RDF.Uri(uri), RDF.Uri(NS_DC + 'creator'), None) \
                == 'http://creativecommons.org')
        except NoValuesFoundError:
            return None
        return License(self.model, uri, self.id)

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
