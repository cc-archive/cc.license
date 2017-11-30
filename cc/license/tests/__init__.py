from __future__ import print_function

from StringIO import StringIO
import lxml.etree
import os

RELAX_PATH = os.path.join(os.path.dirname(__file__), 'schemata')

def relax_validate(schema_filename, instance_buffer):
    """Validates xml string instance_buffer against RelaxNG schema 
       located in file schema_filename. By convention, schema_filename 
       is a constant defined in the test module. Schema files are 
       located in tests/schemata."""

    relaxng = lxml.etree.RelaxNG(lxml.etree.parse(schema_filename))
    instance = lxml.etree.parse(StringIO(instance_buffer))

    if not relaxng.validate(instance):
        print(relaxng.error_log.last_error)
        return False
    else:
        return True

