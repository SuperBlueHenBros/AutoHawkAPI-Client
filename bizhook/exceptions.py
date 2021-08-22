
class BizhawkHookError(Exception):
    """Base error for Bizhawk hook"""


class InvalidRequest(BizhawkHookError):
    """Bizhawk was sent an invalid request"""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

class InvalidResponse(BizhawkHookError):
    """Response did not follow the parseable format"""