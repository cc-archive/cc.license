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
        except KeyError:
            raise CCLicenseError, "Language %s does not exist for jurisdiction %s" % (language, self.code)

class License(object):
    """Base class for ILicense implementation modeling a specific license."""
    zope.interface.implements(interfaces.ILicense)


    """
    license_class = Attribute(u"The license class this license belongs to.")

    name = Attribute(u"The human readable name for this license.")
    version = Attribute(u"The number version for the license.")
    jurisdiction = Attribute(u"The jurisdiction for the license.")
    uri = Attribute(u"The fully qualified URI of the license.")

    current_version = Attribute(u"The ILicense of the current version of "
                                "this jurisdiction + license.")
    deprecated = Attribute(u"Boolean attribute; True if this license is "
                           "deprecated")
    superseded = Attribute(u"Boolean attribute; True if this license has "
                           "been replaced with a newer version.")
    license_code = Attribute(u"The short alpha code for this license.")
    libre = Attribute(u"Returns True if this is a 'Libre' license.")

    """
