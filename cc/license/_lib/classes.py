from distutils.version import StrictVersion

import RDF
import zope.interface
import interfaces 
import rdf_helper

import cc.license
from cc.license.util import locale_dict_fetch_with_fallbacks
from cc.license._lib.exceptions import CCLicenseError


def _sort_licenses(x, y):
    x_version = StrictVersion(x.version)
    y_version = StrictVersion(y.version)

    if x_version > y_version:
        return 1
    elif x_version == y_version:
        return 0
    else:
        return -1


class License(object):
    """Base class for ILicense implementation modeling a specific license."""
    zope.interface.implements(interfaces.ILicense)

    def __init__(self, model, uri):
        # XXX do this as a dict later?
        self._uri = uri
        self._model = model # hang on to the model for lazy queries later
        self._lclass = None
        self._titles = None
        self._descriptions = None
        self._superseded_by = None
        self._version = None
        self._jurisdiction = None
        self._deprecated = None
        self._superseded = None
        self._permits = None
        self._requires = None
        self._prohibits = None
        self._code = None
        self._logos = None

        # make sure the license actually exists
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                  ASK { <%s> rdf:type cc:License . }"""
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        uri_exists = query.execute(self._model).get_boolean()
        if not uri_exists:
            raise CCLicenseError, \
                  "License <%(uri)s> does not exist in model given." % {
                              'uri': self.uri }

    def __repr__(self):
        return "<License object '%(uri)s'>" % {'uri': self.uri}

    def __str__(self):
        return "%(title)s %(version)s %(jurisdiction)s" % {
                             'title': self.title(),
                             'version': self.version,
                             'jurisdiction': self.jurisdiction.title()
                                                          }

    def title(self, language='en'):
        if self._titles is None:
            self._titles = rdf_helper.get_titles(self._model, self.uri)
        return locale_dict_fetch_with_fallbacks(self._titles, language)

    @property
    def license_class(self):
        if self._lclass is None:
            lclass_uri = rdf_helper.get_license_class(self._model, self.uri)
            # XXX this feels hackish
            for value in cc.license.selectors.SELECTORS.values():
                if value.uri == lclass_uri:
                    self._lclass = value.id
        return self._lclass

    # XXX use distutils.version.StrictVersion to ease comparison?
    # XXX return what if nonexistent?
    @property
    def version(self):
        if self._version is None:
            self._version = rdf_helper.get_version(self._model, self.uri)
        return self._version

    # XXX return what if nonexistent?
    @property
    def jurisdiction(self):
        if self._jurisdiction is None:
            self._jurisdiction = rdf_helper.get_jurisdiction(self._model, self.uri)
        return self._jurisdiction

    @property
    def uri(self):
        return str(self._uri) # str, not unicode

    @property
    def current_version(self):
        """
        Get the current version of the license.
        """
        qstring = """
                  PREFIX dc: <http://purl.org/dc/elements/1.1/>

                  SELECT ?license
                  WHERE {
                    ?license dc:identifier '%s' }"""
        query = RDF.Query(
            qstring % self.license_code,
            query_language='sparql')

        license_results = [
            cc.license.by_uri(str(result['license'].uri))
            for result in query.execute(rdf_helper.ALL_MODEL)]

        # only keep results with the same jurisdiction
        license_results = filter(
            lambda lic: lic.jurisdiction == self.jurisdiction, license_results)

        license_results.sort(_sort_licenses)
        return license_results[-1]

    @property
    def deprecated(self):
        if self._deprecated is None:
            self._deprecated = rdf_helper.get_deprecated(self._model, self.uri)
        return self._deprecated

    @property
    def superseded(self):
        if self._superseded is None:
            self._superseded, self._superseded_by = \
                            rdf_helper.get_superseded(self._model, self.uri)
            # just in case superseded_by is needed down the line
        return self._superseded

    @property
    def license_code(self):
        if self._code is None:
            self._code = rdf_helper.get_license_code(self._model, self.uri)
        return self._code

    @property
    def libre(self):
        if self.license_code in ('by', 'by-sa', 'publicdomain'):
            return True
        return False

    @property
    def permits(self):
        if self._permits is None:
            self._permits = rdf_helper.get_permits(self._model, self.uri)
        return self._permits

    @property
    def requires(self):
        if self._requires is None:
            self._requires = rdf_helper.get_requires(self._model, self.uri)
        return self._requires

    @property
    def prohibits(self):
        if self._prohibits is None:
            self._prohibits = rdf_helper.get_prohibits(self._model, self.uri)
        return self._prohibits

    @property
    def logo(self):
        return self.logo_method()

    def logo_method(self, size='88x31'):
        if self._logos is None:
            self._logos = rdf_helper.get_logos(self._model, self.uri)

        if self._logos:
            try:
                return [logo for logo in self._logos if size in logo][0]
            except IndexError:
                return max(self._logos)

    @property
    def rdf(self):
        """
        Gives text of the permission/requirements rdf data.

        Probably shouldn't be used any more, but needed for deed
        templates.
        """
        text = []
        text.append(
            '<rdf:RDF xmlns="http://creativecommons.org/ns#" '
            'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">')
        text.append(
            '  <License rdf:about="%s">' % self.uri)

        permits = list(self.permits)
        permits.sort()
        for permission in permits:
            text.append(
                '    <permits rdf:resource="%s"/>' % permission)

        requires = list(self.requires)
        requires.sort()
        for requirement in requires:
            text.append(
                '    <requires rdf:resource="%s"/>' % requirement)
        
        text.append('  </License>')
        text.append('</rdf:RDF>')

        return '\n'.join(text)


class Question(object):
    zope.interface.implements(interfaces.IQuestion)

    def __init__(self, root, lclass, id):
        """Given an etree root object, a license class string, and a question
           identifier string, populate this Question object with all
           relevant data found in the etree."""
        self._id = id
        self._answers = {}  # key is language

        _flag = False # for error checking
        # xml:lang namespace
        xlang = '{http://www.w3.org/XML/1998/namespace}lang'

        for child in root.getchildren():
            if child.get('id') != lclass:
                continue
            for field in child.findall('field'):
                if field.get('id') != self.id:
                    continue
                _flag = True # throw error if we don't find our lclass and id
                self._labels = {}
                self._descs = {}
                self._enums = {}
                for l in field.findall('label'):
                    self._labels[l.get(xlang)] = l.text
                for d in field.findall('description'):
                    self._descs[d.get(xlang)] = d.text
                for e in field.findall('enum'):
                    eid = e.get('id')
                    elabels = {}
                    for l in e.findall('label'):
                        elabels[l.get(xlang)] = l.text
                    edesc = {} 
                    for d in e.findall('description'):
                        edesc[d.get(xlang)] = d.text
                    self._enums[eid] = (elabels, edesc,)

        if not _flag:
            raise CCLicenseError, "Question identifier %(id)s not found" % \
                    {'id': self.id}

    def __repr__(self):
        return "<Question object id='%(id)s'>" % {'id': self.id}

    def __str__(self):
        return "Question: %(label)s" % {'label': self.label()}
            
    @property
    def id(self):
        return self._id

    def label(self, language='en'):
        if language == '':
            language = 'en' # why not?
        return locale_dict_fetch_with_fallbacks(self._labels, language)

    def description(self, language='en'):
        if language == '':
            language = 'en' # why not?
        return locale_dict_fetch_with_fallbacks(self._descs, language)

    def answers(self, language='en'):
        if self._answers.has_key(language):
            return self._answers[language]

        if language == '':
            language = 'en' # why not?
            
        answers = []
        for k in self._enums.keys():
            label = locale_dict_fetch_with_fallbacks(self._enums[k][0],
                                                     language)
            # is there a description for this enum?
            if self._enums[k][1] != {}: 
                # create a tuple with a localized description
                enum = ( label, k,
                         locale_dict_fetch_with_fallbacks(self._enums[k][1],
                                                         language) )
            else:
                enum = ( label, k, None)
                
            answers.append(enum)
            
        self._answers[language] = answers

        return answers
