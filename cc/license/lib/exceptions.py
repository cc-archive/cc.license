"""Exceptions for errors specific to cc.license.
   When you mess up dealing with ..  """

class RdfHelperError(Exception):
    pass

class NoValuesFoundError(RdfHelperError):
    """Raised when an RDF query returns no values."""
    pass
