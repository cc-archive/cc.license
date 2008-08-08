
import zope.interface
import cc.license
from cc.license._lib import interfaces, rdf_helper
from cc.license._lib.classes import License, Question
from cc.license._lib.exceptions import CCLicenseError

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
                            'nc-sampling+',
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

    def __init__(self, uri):
        """Generates a LicenseSelector instance from a given URI.
           First it parses the RDF to get all information in there.
           Then it has to go to questions.xml to get the rest.
           In the questions.xml will be deprecated later, with all
           that information moving to RDF."""
        self._uri = uri
        self._model = rdf_helper.ALL_MODEL
                      # plenty of room for optimization...
        self._licenses = {}
        self._id = None
        self._titles = None

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

    def __repr__(self):
        return "<LicenseSelector id='%s'>" % self.id

    def __str__(self):
        return "(%s Selector)" % self.title()

    @property
    def id(self):
        if self._id is None:
            self._id = rdf_helper.get_selector_id(self.uri)
        return self._id

    @property
    def uri(self):
        return self._uri

    def title(self, language='en'):
        if self._titles is None:
            self._titles = rdf_helper.get_titles(rdf_helper.SEL_MODEL, self.uri)
        return self._titles[language]

    def by_uri(self, uri):
        # error checking
        if not uri.startswith('http://creativecommons.org/licenses/'):
            raise CCLicenseError, "Invalid license URI."
        if uri not in self._licenses:
            self._licenses[uri] = License(self._model, uri)
        return self._licenses[uri]

    def by_code(self, license_code, jurisdiction=None, version=None):
        if not validate(self.id, license_code):
            raise CCLicenseError, \
                  "License code %s is invalid for selector %s" % \
                  (license_code, self.id)
        uri = cc.license._lib.dict2uri(dict(jurisdiction=jurisdiction,
                                            version=version,
                                            code=license_code))
        return self.by_uri(uri)

    def questions(self):
        return list(self._questions)

    ## Yet Another Hack
    ## Unsure where the answers-into-license-code data and logic ought to go.
    ## In the old api, it's an XSLT document, which feels wrong.
    ## I believe it should be in the equivalent of questions.xml.
    ## Until then, each class gets its own hard-coded handler.

    # TODO: refactor error-checking code into validation method that
    # checks the answers_dict against questions()

    # default behavior is to ignore extra answers
    def by_answers(self, answers_dict):
        license_code = {'standard' : self._by_answers_standard,
                        'recombo' : self._by_answers_recombo,
                        'publicdomain' : self._by_answers_publicdomain,
                       }[self.id](answers_dict)
        # get jurisdiction separately
        try:
            jurisdiction = answers_dict['jurisdiction']
        except KeyError:
            jurisdiction = None
        return self.by_code(license_code, jurisdiction=jurisdiction)

    # TODO: handle 1.0 license weirdness (out-of-order license code)
    def _by_answers_standard(self, answers_dict):
        pieces = ['by']
        # error checking
        for s in ('commercial', 'derivatives'):
            if s not in answers_dict.keys():
                raise CCLicenseError, "Invalid question answered."
        for id, values in ( ('commercial', ['y', 'n']),
                            ('derivatives', ['y', 'sa', 'n']) ):
            if answers_dict[id] not in values:
                raise CCLicenseError, "Invalid answer given."
        # create license code
        if answers_dict['commercial'] == 'n':
            pieces.append('nc')
        if answers_dict['derivatives'] == 'n':
            pieces.append('nd')
        if answers_dict['derivatives'] == 'sa':
            pieces.append('sa')
        return '-'.join(pieces)

    def _by_answers_recombo(self, answers_dict):
        if 'sampling' not in answers_dict.keys():
            raise CCLicenseError, "Invalid question answered."
        a = answers_dict['sampling']
        try:
            return {
                    'sampling' : 'sampling',
                    'samplingplus' : 'sampling+',
                    'ncsamplingplus' : 'nc-sampling+',
                   }[a]
        except KeyError:
            raise CCLicenseError, "Invalid answer given."

    def _by_answers_publicdomain(self, answers_dict):
        return 'publicdomain'
