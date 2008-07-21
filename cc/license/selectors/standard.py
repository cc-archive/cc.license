import re
import zope.interface
import glob
import os
import RDF
import cc.license
from cc.license.lib.classes import License
from cc.license.lib.interfaces import ILicenseSelector
from cc.license.lib.rdf_helper import query_to_single_value, NS_DC
from cc.license.lib.exceptions import NoValuesFoundError
from cc.license.lib import rdf_helper

