
import zope.interface
import cc.license
from cc.license.lib import interfaces, rdf_helper
from cc.license.lib.classes import License, Question

# MAJOR TEMPORARY HACK
# So hopefully at some point soon in the future, each License described
# in the RDF files will have a property, something like cc:licenseCode
# (see selectors.rdf), which will say which LicenseSelector that particular
# License is associted with. Until then, we enumerate here.
# OPEN QUESTION: what about all the weird licenses that aren't below?
valid_codes = {
               'standard' : [
                             'by-nc-nd',
                             'by-nc-sa',
                             'by-nc',
                             'by-nd',
                             'by-sa',
                             'by',
                            ],
               'recombo' : [
                            'sampling+',
                            'sampling',
                           ],
               'publicdomain' : [
                                 'publicdomain',
                                ],
              }

def validate(selector_id, license_code):
    for code in valid_codes[selector_id]:
        if code == license_code:
            return True
    return False

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

        # TODO: refactor this somewhere?
        # populate questions from questions.xml
        self._questions = []
        for child in rdf_helper.questions_root.getchildren():
            if child.get('id') != self.id:
                continue
            for field in child.findall('field'):
                fid = field.get('id')
                self._questions.append( 
                     Question(rdf_helper.questions_root,
                                         self.id, fid))

    @property
    def id(self):
        return self._id

    @property
    def uri(self):
        return self._uri

    @property
    def jurisdictions(self):
        raise NotImplementedError

    @property
    def versions(self):
        raise NotImplementedError

    def title(self, language='en'):
        return self._titles[language]

    def by_uri(self, uri):
        if uri not in self._licenses:
            self._licenses[uri] = License(self._model, uri, self.id)
        return self._licenses[uri]

    def by_code(self, license_code, jurisdiction=None, version=None):
        if not validate(self.id, license_code):
            raise CCLicenseError, \
                  "License code %s is invalid for selector %s" % \
                  (license_code, self.id)
        uri = cc.license.lib.dict2uri(dict(jurisdiction=jurisdiction,
                                           version=version,
                                           code=license_code))
        return self.by_uri(uri)

    def by_answers(self, answers_dict):
        raise NotImplementedError

    def questions(self):
        return self._questions
