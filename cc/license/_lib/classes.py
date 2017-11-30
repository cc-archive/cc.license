from __future__ import absolute_import
from builtins import str
from builtins import object
import RDF
import zope.interface

from cc.i18n.gettext_i18n import ugettext_for_locale
from cc.i18n.util import locale_to_lower_upper
from cc.i18n import mappers

import cc.license
from cc.license.util import locale_dict_fetch_with_fallbacks
from cc.license._lib import interfaces
from cc.license._lib import rdf_helper
from cc.license._lib.exceptions import SelectorQAError, ExistentialException
from cc.license._lib.functions import all_possible_license_versions
from cc.licenserdf.util import inverse_translate

class License(object):
    """Base class for ILicense implementation modeling a specific license."""
    zope.interface.implements(interfaces.ILicense)

    def __init__(self, uri):
        # XXX do this as a dict later?
        self._uri = uri
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
        self._legalcodes = {}

        # make sure the license actually exists
        qstring = """
                  PREFIX cc: <http://creativecommons.org/ns#>
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                  ASK { <%s> rdf:type cc:License . }"""
        query = RDF.Query(qstring % self.uri, query_language='sparql')
        uri_exists = query.execute(rdf_helper.ALL_MODEL).get_boolean()
        if not uri_exists:
            raise ExistentialException("License <%(uri)s> does not exist in model given." % {
                              'uri': self.uri })

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
            self._titles = rdf_helper.get_titles(self.uri)
        i18n_title = self._titles['x-i18n']
        return inverse_translate(i18n_title, locale_to_lower_upper(language))

    @property
    def license_class(self):
        if self._lclass is None:
            lclass_uri = rdf_helper.get_license_class(self.uri)
            # XXX this feels hackish
            for value in list(cc.license.selectors.SELECTORS.values()):
                if value.uri == lclass_uri:
                    self._lclass = value.id
        return self._lclass

    # XXX use distutils.version.StrictVersion to ease comparison?
    # XXX return what if nonexistent?
    @property
    def version(self):
        if self._version is None:
            self._version = rdf_helper.get_version(self.uri)
        return self._version

    # XXX return what if nonexistent?
    @property
    def jurisdiction(self):
        if self._jurisdiction is None:
            self._jurisdiction = rdf_helper.get_jurisdiction(self.uri)
        return self._jurisdiction

    @property
    def uri(self):
        return str(self._uri) # str, not unicode

    @property
    def current_version(self):
        """
        Get the current version of the license.
        """
        license_results = all_possible_license_versions(
            self.license_code, self.jurisdiction.code)

        return license_results[-1]

    @property
    def deprecated(self):
        if self._deprecated is None:
            self._deprecated = rdf_helper.get_deprecated(self.uri)
        return self._deprecated

    @property
    def superseded(self):
        if self._superseded is None:
            self._superseded, self._superseded_by = rdf_helper.get_superseded(
                self.uri)
            # just in case superseded_by is needed down the line
        return self._superseded

    @property
    def license_code(self):
        if self._code is None:
            self._code = rdf_helper.get_license_code(self.uri)
        return self._code

    @property
    def libre(self):
        if self.license_code in ('by', 'by-sa', 'publicdomain'):
            return True
        return False

    @property
    def permits(self):
        if self._permits is None:
            self._permits = rdf_helper.get_permits(self.uri)
        return self._permits

    @property
    def requires(self):
        if self._requires is None:
            self._requires = rdf_helper.get_requires(self.uri)
        return self._requires

    @property
    def prohibits(self):
        if self._prohibits is None:
            self._prohibits = rdf_helper.get_prohibits(self.uri)
        return self._prohibits

    @property
    def logo(self):
        return self.logo_method()

    def logo_method(self, size='88x31'):
        if self._logos is None:
            self._logos = rdf_helper.get_logos(self.uri)

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


    def legalcodes(self, language='en'):
        """
        Return a list of
        [(legalcode_uri, legalcode_lang, legalcode_lang_translated)]
        for this license.

        If this is a single-legalcode option, it'll probably return
        [(legalcode_uri, None, None)]

        """
        if language in self._legalcodes:
            return self._legalcodes[language]

        gettext = ugettext_for_locale(language)

        legalcodes = set()
        for legalcode, lang in rdf_helper.get_license_legalcodes(self.uri):
            if lang is None:
                translated_lang = None
            # <terrible_fixable_hacks>
            # We should probably add lang.sr_CYRL and lang.sr_LATN messages
            elif lang == 'sr-Cyrl':
                translated_lang = gettext('Serbian')
            elif lang == 'sr-Latn':
                translated_lang = 'srpski (latinica)'
            # </terrible_fixable_hacks>
            else:
                translated_lang = gettext(
                    mappers.LANG_MAP[locale_to_lower_upper(lang)])

            legalcodes.add(
                (legalcode, lang, translated_lang))

        self._legalcodes[language] = legalcodes

        return legalcodes


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
            raise SelectorQAError("Question identifier %(id)s not found" % \
                    {'id': self.id})

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
        if language in self._answers:
            return self._answers[language]

        if language == '':
            language = 'en' # why not?
            
        answers = []
        for k in list(self._enums.keys()):
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


class JurisdictionQuestion(object):
    """
    The Question object works off of questions.xml, but jurisdiction
    information is kept up to date in jurisdictions.rdf, so we should
    pull from there for jurisdiction questions.
    """
    #zope.interface.implements(interfaces.IQuestion)

    def __init__(self, lclass, lclass_uri):
        """
        Keyword arguments:
        - lclass: The license class of the parent selector, ie 'standard'
        - lclass_uri: The license class url, ie
          'http://creativecommons.org/license/'
        """
        self.id = 'jurisdiction'

        self._lclass = lclass
        self._lclass_uri = lclass_uri
        self._jurisdictions = rdf_helper.jurisdictions_for_selector(
            self._lclass_uri)
        self._answers = {}

    def __repr__(self):
        return "<JurisdictionQuestion object id='%(id)s'>" % {'id': self.id}

    def __str__(self):
        return "JurisdictionQuestion: %(label)s" % {'label': self.label()}
            
    def label(self, language='en'):
        if language == '':
            language = 'en' # why not?

        gettext = ugettext_for_locale(language)
        return gettext("Jurisdiction of your license")

    def description(self, language='en'):
        if language == '':
            language = 'en' # why not?

        gettext = ugettext_for_locale(language)
        return gettext(
            """\
Use the option "International" if you desire a license using language
and terminology from international treaties.  If the licenses have
been ported to your jurisdiction and you feel that your jurisdiction's
ported licenses account for some aspect of local legislation that the
international licenses do not, then you may want to consider
<a href="http://wiki.creativecommons.org/Frequently_Asked_Questions#Should_I_choose_an_international_license_or_a_ported_license.3F">which
license is better suited for your needs</a>.""")

    def answers(self, language='en'):
        if language == '':
            language = 'en' # why not?
            
        gettext = ugettext_for_locale(language)

        answers = []
        for jurisdiction in self._jurisdictions:
            # Answers format is
            # (label, id/key, description)
            # And jurisdictions don't need a description ;)
            juris_code = str(jurisdiction.rstrip('/').split('/')[-1])
            answers.append(
                (gettext(mappers.COUNTRY_MAP[juris_code.lower()]),
                 juris_code, None))

        answers = sorted(answers, key=lambda answer: answer[1])

        if answers:
            answers = [(gettext('International'), '', None)] + answers

        return answers
