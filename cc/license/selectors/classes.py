
import zope.interface
import cc.license
from cc.license.lib import interfaces, rdf_helper
from cc.license.lib.classes import License

class LicenseSelector:
    zope.interface.implements(interfaces.ILicenseSelector)

    def __init__(self, uri, license_code):
        """Generates a LicenseSelector instance from a given URI.
           First it parses the RDF to get all information in there.
           Then it has to go to questions.xml to get the rest.
           In the questions.xml is soon to be deprecated, with all
           that information moving to RDF."""
        self._uri = uri
        self._id = license_code
        self._titles = rdf_helper.get_titles(rdf_helper.SEL_MODEL, self.uri)
        self._model = rdf_helper.ALL_MODEL
                      # plenty of room for optimization...
        self._licenses = {}

    @property
    def uri(self):
        return self._uri

    @property
    def id(self):
        return self._id

    def title(self, language='en'):
        return self._titles[language]

    def by_uri(self, uri):
        if uri not in self._licenses:
            self._licenses[uri] = License(self._model, uri, self.id)
        return self._licenses[uri]

    def by_code(self, license_code, jurisdiction=None, version=None):
        # HACK: publicdomain is special
        if self.id == 'publicdomain':
            uri = 'http://creativecommons.org/licenses/publicdomain/'
        else:
            uri = cc.license.lib.dict2uri(dict(jurisdiction=jurisdiction,
                                               version=version,
                                               code=license_code))
        return self.by_uri(uri)

    def by_answers(self, answers_dict):
        raise NotImplementedError

    def questions(self):
        raise NotImplementedError

