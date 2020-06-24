class RDException(BaseException):
    """Base Redirector exception."""
    name = 'Redirector exception'


class RDTooManyRedirectsException(RDException):
    """Too many redirects."""
    msg = 'Too many redirects.'


class RDCycleRedirectsException(RDException):
    """Redirects are cycled."""
    msg = 'Redirects are cycled.'


class RDTooBigBodyException(RDException):
    """Response body is too big."""
    msg = 'Response body is too big.'
