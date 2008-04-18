import zope.interface
from cc.license.interfaces import ILicenseSelector, ILicense
from cc.license.rdf_helper import query_to_single_value, NS_DC, NS_DCQ

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
            default=None)
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

class Selector(object):
    zope.interface.implements(ILicenseSelector)
    id = "Selector for sampling licenses"
    def __init__(self):
        files = glob.glob(os.path.join(cc.license.rdf_helper.LIC_RDF_PATH ,'*sampling*'))
        self.model = cc.license.rdf_helper.init_model(*files)
        self.jurisdictions = None # FIXME
        self.versions = None # FIXME
    def by_uri(self, uri):
        return SamplingLicense(self.model, uri)
    def by_code(self, license_code, jurisdiction = None, version = None):
        base = 'http://creativecommons.org/licenses/' + license_code + '/'
        if not version:
            version = '1.0'
        base += '/' + version + '/'
        if jurisdiction:
            base += '/' + jurisdiction + '/'
        return self.by_uri(base)
    def by_answers(self, answers_dict):
        raise NotImplementedException
    def questions(self):
        raise NotImplementedException
            
