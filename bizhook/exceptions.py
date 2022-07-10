
class BizhawkHookError(Exception):
    """Base error for Bizhawk hook"""


class InvalidRequest(BizhawkHookError):
    """Bizhawk was sent an invalid request"""

    def __init__(self, code, message):
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message

class InvalidResponse(BizhawkHookError):
    """Response did not follow the parseable format"""