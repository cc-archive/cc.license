import RDF
import zope.interface
import interfaces 
import rdf_helper

class Jurisdiction(object):
    zope.interface.implements(interfaces.IJurisdiction)
    def __init__(self, short_name):
        '''@param short_name can be e.g. mx'''
        model = rdf_helper.init_model(
            rdf_helper.JURI_RDF_PATH)

        self.code = short_name
        self.id = 'http://creativecommons.org/international/%s/' % short_name
        id_uri = RDF.Uri(self.id)
        self.local_url = rdf_helper.query_to_single_value(model,
            id_uri, RDF.Uri(rdf_helper.NS_CC + 'jurisdictionSite'), None)
        self.launched = rdf_helper.query_to_single_value(model,
            id_uri, RDF.Uri(rdf_helper.NS_CC + 'launched'), None)
