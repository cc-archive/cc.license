"""Exceptions for errors specific to cc.license.
   When you mess up dealing with ..  """

class RdfHelperError(Exception):
    pass

class NoValuesFoundError(RdfHelperError):
    """Raised when an RDF query returns no values."""
    pass

class CCLicenseError(Exception):
    """Generic exception when misuse cc.license"""
    pass

class MalformedURIError(CCLicenseError):
    """Raised when a URI is unusuable because of it being formatted wrong."""
    pass

class SelectorQAError(CCLicenseError):
    """Raised when a question or answer is invalid."""
    pass

class ExistentialException(CCLicenseError):
    """Raised when something requested doesn't exist, or when you wondering
    what is the point if it all ends the same way."""
    pass
