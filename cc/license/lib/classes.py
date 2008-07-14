import RDF
import zope.interface
import interfaces 
import rdf_helper
from cc.license.lib.exceptions import NoValuesFoundError, CCLicenseError

# define model out here in the name of efficiency
# XXX but in the long run this is likely a poor choice
model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)

class Jurisdiction(object):
    zope.interface.implements(interfaces.IJurisdiction)
    def __init__(self, short_name):
        """Creates an object representing a jurisdiction.
           short_name is a (usually) two-letter code representing
           the same jurisdiction; for a complete list, see
           cc.license.jurisdiction_codes()"""
        self.code = short_name
        self.id = 'http://creativecommons.org/international/%s/' % short_name
        self._langs = self._build_langs()
        id_uri = RDF.Uri(self.id)
        try:
            self.local_url = rdf_helper.query_to_single_value(model,
                id_uri, RDF.Uri(rdf_helper.NS_CC + 'jurisdictionSite'), None)
        except NoValuesFoundError:
            self.local_url = None
        try: 
            self.launched = rdf_helper.query_to_single_value(model,
                id_uri, RDF.Uri(rdf_helper.NS_CC + 'launched'), None)
        except NoValuesFoundError:
            self.launched = None

    def _build_langs(self):
        qstring = """
                     PREFIX cc: <http://creativecommons.org/ns#>
                     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                     PREFIX dc: <http://purl.org/dc/elements/1.1/>
                     PREFIX int: <http://creativecommons.org/international/">

                     SELECT ?title
                     WHERE
                      {
                         <%s> dc:title ?title .
                      }
                  """
        # get the data back
        query = RDF.Query(qstring % self.id, query_language='sparql')
        solns = list(query.execute(model))
        # parse the data
        _langs = {}
        for s in solns:
            tmp = s['title'].literal_value
            _langs[ tmp['language'] ] = tmp['string']
        return _langs

    def title(self, language='en'):
        try:
            return self._langs[language]
        except KeyError, e:
            import sys
            tb = sys.exc_info()[2]
            msg = "Language %s does not exist for jurisdiction %s"
            raise CCLicenseError, msg % (language, self.code), tb

class License(object):
    """Base class for ILicense implementation modeling a specific license."""
    zope.interface.implements(interfaces.ILicense)

    # XXX where does license_class information come from?

    def __init__(self, model, uri):
        pass

    def name(self, language='en'):
        return self._names[language]
