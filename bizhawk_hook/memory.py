
class Memory:
    """Client for reading from and writing to Bizhawk memory"""

    def __init__(self, address: str = '127.0.0.1', port: int = 16154):
        self.address = address
        self.port = port