import RDF
import zope.interface
import interfaces 
import rdf_helper
from cc.license.lib.exceptions import NoValuesFoundError, CCLicenseError

# define model out here in the name of efficiency
# XXX but in the long run this is likely a poor choice
juri_model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)

# TODO: make it accept either a valid URI or short code!
class Jurisdiction(object):
    zope.interface.implements(interfaces.IJurisdiction)
    def __init__(self, short_name):
        """Creates an object representing a jurisdiction.
           short_name is a (usually) two-letter code representing
           the same jurisdiction; for a complete list, see
           cc.license.jurisdiction_codes()"""
        self.code = short_name
        self.id = 'http://creativecommons.org/international/%s/' % short_name
        self._titles = rdf_helper.get_titles(juri_model, self.id)
        id_uri = RDF.Uri(self.id)
        try:
            self.local_url = rdf_helper.query_to_single_value(juri_model,
                id_uri, RDF.Uri(rdf_helper.NS_CC + 'jurisdictionSite'), None)
        except NoValuesFoundError:
            self.local_url = None
        try: 
            self.launched = rdf_helper.query_to_single_value(juri_model,
                id_uri, RDF.Uri(rdf_helper.NS_CC + 'launched'), None)
        except NoValuesFoundError:
            self.launched = None

    def title(self, language='en'):
        try:
            return self._titles[language]
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
        self.uri = uri
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>
                  PREFIX dcq: <http://purl.org/dc/terms/>               
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                  SELECT ?deprecatedDate ?version ?replacement ?jurisdiction
                  WHERE {
                         <%s> rdf:type cc:License .
                         <%s> dcq:hasVersion ?version .
                         OPTIONAL { <%s> cc:deprecatedOn ?deprecatedDate }
                         OPTIONAL { <%s> dcq:isReplacedBy ?replacement }
                         OPTIONAL { <%s> cc:jurisdiction ?jurisdiction }
                        }"""
        qstring = qstring % ((uri,) * 5) # XXX there's got to be a better way
        query = RDF.Query(qstring, query_language='sparql')
        solns = list(query.execute(model))
        if len(solns) != 1:
            raise CCLicenseError, \
                  "Got %d solutions for <%s> (expecting 1)" % (len(solns), uri)

        soln = solns[0]
        # start populating properties
        # TODO: tests for exercising EACH of these properties
        self.jurisdiction = str(soln['jurisdiction'].uri)
            # TODO: jurisdiction object instead of string?
        self.version = soln['version'].literal_value['string']
        self.deprecated = soln['deprecatedDate'] is not None
        self.superseded = soln['replacement'] is not None

        # TODO: license_class, libre, current_version, license_code

        self._titles = rdf_helper.get_titles(model, uri)

    def title(self, language='en'):
        return self._titles[language]
