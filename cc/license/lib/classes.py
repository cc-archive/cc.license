import RDF
import zope.interface
import interfaces 
import rdf_helper

import cc.license
from cc.license.lib.exceptions import NoValuesFoundError, CCLicenseError
from cc.license.jurisdictions import uri2code

# define model out here in the name of efficiency
# XXX but in the long run this is likely a poor choice
juri_model = rdf_helper.init_model(rdf_helper.JURI_RDF_PATH)

class Jurisdiction(object):
    zope.interface.implements(interfaces.IJurisdiction)
    def __init__(self, uri):
        """Creates an object representing a jurisdiction, given
           a valid jurisdiction URI. For a complete list, see
           cc.license.jurisdictions.list_uris()"""
        if not uri.startswith('http://creativecommons.org/international/') \
           or not uri.endswith('/'):
            raise CCLicenseError, "Malformed jurisdiction URI: <%s>" % uri
        self.code = uri2code(uri)
        self.id = uri
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

    def __init__(self, model, uri, license_class):
        self._uri = uri
        self._model = model # hang on to the model for lazy queries later
        self._lclass = license_class # defined by Selector
        self._titles = None
        self._descriptions = None
        self._superseded_by = None

        # make sure the license actually exists
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                  ASK { <%s> rdf:type cc:License . }"""
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        uri_exists = query.execute(model).get_boolean()
        if not uri_exists:
            raise CCLicenseError, \
                  "License <%s> does not exist in model given." % self.uri

    def title(self, language='en'):
        if self._titles is None:
            self._titles = rdf_helper.get_titles(self._model, self.uri)
        return self._titles[language]

    def description(self, language='en'):
        if self._descriptions is None:
            self._descriptions = rdf_helper.get_descriptions(
                                           self._model, self.uri)
        if self._descriptions == '':
            return ''
        else:
            return self._descriptions[language]

    @property
    def license_class(self):
        return self._lclass

    # XXX use distutils.version.StrictVersion to ease comparison?
    @property
    def version(self):
        qstring = """
                  PREFIX dcq: <http://purl.org/dc/terms/>

                  SELECT ?version
                  WHERE {
                         <%s> dcq:hasVersion ?version .
                        }
                  """
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        solns = list(query.execute(self._model))
        if len(solns) == 0:
            return '' # XXX return what if nonexistent?
        else:
            return solns[0]['version'].literal_value['string']

    @property
    def jurisdiction(self):
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>

                  SELECT ?jurisdiction
                  WHERE {
                         <%s> cc:jurisdiction ?jurisdiction .
                        }
                  """
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        solns = list(query.execute(self._model))
        if len(solns) == 0:
            return '' # XXX return what if nonexistent?
        else:
            return str(solns[0]['jurisdiction'].uri)

    @property
    def uri(self):
        return self._uri

    # TODO: implement!
    # TODO: write tests!
    @property
    def current_version(self):
        return ''

    @property
    def deprecated(self):
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                  ASK { <%s> cc:deprecatedOn ?date . }"""
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        self._deprecated = query.execute(self._model).get_boolean()
        return self._deprecated

    @property
    def superseded(self):
        qstring = """
                  PREFIX dcq: <http://purl.org/dc/terms/>

                  SELECT ?replacement
                  WHERE {
                         <%s> dcq:isReplacedBy ?replacement .
                        }
                  """
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        solns = list(query.execute(self._model))
        if len(solns) == 0:
            return False
        else:
            self._superseded_by = str(solns[0]['replacement'].uri)
            return True

    @property
    def license_code(self):
        return cc.license.lib.code_from_uri(self.uri)

    # TODO: implement!
    # TODO: write tests!
    @property
    def libre(self):
        return False

