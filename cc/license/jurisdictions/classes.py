from builtins import object
from rdflib import URIRef

import cc.license
from cc.license._lib.exceptions import NoValuesFoundError, InvalidURIError
from cc.license._lib import rdf_helper

class Jurisdiction(object):

    def __init__(self, jurisdictionUri):
        """Creates an object representing a jurisdiction, given
           a valid jurisdiction URI. For a complete list, see
           cc.license.jurisdictions.list_uris()"""
        self._default_language = None
        self.uri = jurisdictionUri

        if self.uri == '': # handle default jurisdiction case
            self.code = ''
            self.jurisdiction_id = ''
            self._titles = {'en':'Unported'} # FIXME
            self.local_url = ''
            self.launched = True
            return
        if not self.uri.startswith(
                'http://creativecommons.org/international/') \
            or not self.uri.endswith('/'):
            raise InvalidURIError("Invalid jurisdiction URI: <%s>" % self.uri)
        self.code = cc.license.jurisdictions.uri2code(self.uri)
        self._titles = rdf_helper.get_titles(self.uri, rdf_helper.JURI_MODEL)
        id_uri = URIRef(self.uri)
        try:
            self.local_url = rdf_helper.query_to_single_value(
                id_uri, URIRef(rdf_helper.NS_CC + 'jurisdictionSite'),None)
        except NoValuesFoundError:
            self.local_url = None
        try:
            self.launched = rdf_helper.query_to_single_value(
                id_uri, URIRef(rdf_helper.NS_CC + 'launched'), None)
        except NoValuesFoundError:
            self.launched = None

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.uri == other.uri and \
               self.code == other.code and \
               self.local_url == other.local_url and \
               self.title() == other.title() and \
               self.launched == other.launched

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.uri == '':
            return "<Jurisdiction object (%s)>" % (self.title())
        else:
            return "<Jurisdiction object '%s' (%s)>" % (self.uri, self.title())

    def __str__(self):
        if self.uri == '':
            return self.title() + " (No jurisdiction)"
        else:
            return "%s (%s)" % (self.title(), self.code)

    def __hash__(self):
        return hash((self.uri, self.code, self.local_url,
                     self.title(), self.launched))

    def title(self, language='en'):
        try:
            return cc.license.util.locale_dict_fetch_with_fallbacks(
                self._titles, language)
        except KeyError as e:
            import sys
            tb = sys.exc_info()[2]
            raise InvalidURIError(
                "Language %s does not exist for jurisdiction %s"
                % (language, self.code), tb)

    @property
    def default_language(self):
        if self._default_language:
            return self._default_language

        self._default_language = rdf_helper.get_jurisdiction_default_language(
            self.uri)
        return self._default_language
