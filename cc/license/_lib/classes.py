import RDF
import zope.interface
import interfaces 
import rdf_helper

import cc.license
from cc.license._lib.exceptions import NoValuesFoundError, CCLicenseError
from cc.license.jurisdictions import uri2code

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
        j = None
        if self.jurisdiction != cc.license.jurisdictions.by_code(''):
            j = cc.license.jurisdictions.uri2code(self.jurisdiction.id)
        return cc.license._lib.current_version(self.license_code, j)

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
        if self._logos is None:
            self._logos = rdf_helper.get_logos(self._model, self.uri)

        if self._logos:
            return max(self._logos)


class Question(object):
    zope.interface.implements(interfaces.IQuestion)

    def __init__(self, root, lclass, id):
        """Given an etree root object, a license class string, and a question
           identifier string, populate this Question object with all
           relevant data found in the etree."""
        self._id = id

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
                    self._enums[eid] = elabels

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
        return self._labels[language]

    def description(self, language='en'):
        if language == '':
            language = 'en' # why not?
        return self._descs[language]

    def answers(self, language='en'):
        if language == '':
            language = 'en' # why not?
        return [ ( self._enums[k][language], k ) 
                 for k in self._enums.keys() ]
