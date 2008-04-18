import RDF
import zope.interface
import cc.license
import cc.license.interfaces
import cc.license.rdf_helper

class Jurisdiction(object):
    zope.interface.implements(cc.license.interfaces.IJurisdiction)
    def __init__(self, short_name):
        '''@param short_name can be e.g. mx'''
        model = cc.license.rdf_helper.init_model(
            cc.license.rdf_helper.JURI_RDF_PATH)

        self.code = short_name
        self.id = 'http://creativecommons.org/international/%s/' % short_name
        id_uri = RDF.Uri(self.id)
        self.local_url = cc.license.rdf_helper.query_to_single_value(model,
            id_uri, RDF.Uri(cc.license.rdf_helper.NS_CC + 'jurisdictionSite'), None)
        self.launched = cc.license.rdf_helper.query_to_single_value(model,
            id_uri, RDF.Uri(cc.license.rdf_helper.NS_CC + 'launched'), None)
