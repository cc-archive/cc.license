import zope.interface
import cc.license
from cc.license._lib import interfaces, rdf_helper
from cc.license._lib.classes import License, Question
from cc.license._lib.exceptions import CCLicenseError


# Cache by_code results via the key:
# (selector.uri, license_code, jurisdiction, version)
SELECTOR_BY_CODE_CACHE = {}


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
        
        self._by_answers  = {
            'standard' : self._by_answers_standard,
            'recombo'  : self._by_answers_recombo,
            'zero'     : self._by_answers_generic('CC0'),
            }.get(self.id) or self._by_answers_generic(self.id)
        

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
        return cc.license.util.locale_dict_fetch_with_fallbacks(
            self._titles, language)

    def by_uri(self, uri):
        # error checking
        if not rdf_helper.selector_has_license(self._model, self.uri, uri):
            raise CCLicenseError, "Invalid license URI."
        if uri not in self._licenses or self._licenses[uri] is None:
            self._licenses[uri] = License(self._model, uri)
        return self._licenses[uri]

    def by_code(self, license_code, jurisdiction=None, version=None):
        cache_key = (self.uri, license_code, jurisdiction, version)
        # Do we have the license cached already?
        if SELECTOR_BY_CODE_CACHE.has_key(cache_key):
            return SELECTOR_BY_CODE_CACHE[cache_key]

        uri = cc.license._lib.dict2uri(dict(jurisdiction=jurisdiction,
                                            version=version,
                                            code=license_code))
        if not self.has_license(uri):
            # old *nc-nd licenses were actually ordered nd-nc.  Try
            # for searching for those if appropriate
            if 'nc-nd' in license_code:
                # See if this works!
                uri = cc.license._lib.dict2uri(
                    dict(jurisdiction=jurisdiction,
                         version=version,
                         code=license_code.replace('nc-nd', 'nd-nc')))
                if not self.has_license(uri):
                    raise CCLicenseError, \
                        "License code '%s' is invalid for selector %s" % \
                        (license_code, self.id)
            else:
                raise CCLicenseError, \
                    "License code '%s' is invalid for selector %s" % \
                    (license_code, self.id)

        license = self.by_uri(uri)
        SELECTOR_BY_CODE_CACHE[cache_key] = license

        return license

    def questions(self):
        return list(self._questions)

    def has_license(self, license_uri):
        if license_uri in self._licenses.keys():
            return True
        else:
            if not rdf_helper.selector_has_license(
                       self._model, self.uri, license_uri):
                return False
            else:
                self._licenses[license_uri] = None
                return True

    def _validate_answers(self, answers_dict):
        
        for q in self.questions():
            # verify that all questions are answered 
            if q.id not in answers_dict.keys():
                raise CCLicenseError, "Invalid question answered."
            # verify that answers have an acceptable value
            # l,v,d = label, value, description :: for each acceptable answer
            if answers_dict[q.id] not in [ v for l,v,d in q.answers() ]:
                raise CCLicenseError, "Invalid answer given."

        return "Bears shit in the woods." is not False

    # default behavior is to ignore extra answers
    def by_answers(self, answers_dict):
        """ uses the handler function set in the constructor """
        # ensure 'jurisdiction' is always a key in the dict
        jurisdiction = answers_dict.setdefault('jurisdiction', '')
        # throw an exception if answers_dict is bunk
        self._validate_answers(answers_dict)
        # return a license code based on answers to this selector's questions 
        license_code = self._by_answers(answers_dict)
        # give back a license object based on the answers 
        return self.by_code(license_code, jurisdiction=jurisdiction)

    # TODO: handle 1.0 license weirdness (out-of-order license code)
    def _by_answers_standard(self, answers_dict):
        
        pieces = ['by']
        
        # create license code
        if answers_dict['commercial'] == 'n':
            pieces.append('nc')
        if answers_dict['derivatives'] == 'n':
            pieces.append('nd')
        if answers_dict['derivatives'] == 'sa':
            pieces.append('sa')

        return '-'.join(pieces)

    def _by_answers_recombo(self, answers_dict):

        return {
            'sampling' : 'sampling',
            'samplingplus' : 'sampling+',
            'ncsamplingplus' : 'nc-sampling+',
            }[ answers_dict['sampling'] ]
        
    def _by_answers_generic(self, license_code):
        """ function factory for license classes that don't require
        any answers processing logic (zero, publicdomain, software) """
        def returns_license_code(answers_dict):
            """ just return the license code """
            return license_code

        return returns_license_code
