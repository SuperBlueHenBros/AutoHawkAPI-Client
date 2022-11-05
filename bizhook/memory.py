from socket import AF_INET, SOCK_STREAM, SHUT_RDWR
from socket import socket as Socket
from socket import create_connection

from .exceptions import InvalidRequest, InvalidResponse

FORM = {
    "INPUT": 0,
    "READ": 1,
    "WRITE": 2,
    "CLIENT": 3
}
'''
Planned:
emulator:
    load rom
    reset?
'''

DELIMITER = '/'

# BUTTON_TRANSLATE = {
#     "P1 A": 0,
#     "P1 B": 1,
#     "P1 Down": 2,
#     "P1 Left": 3,
#     "P1 Right": 4,
#     "P1 Select": 5,
#     "P1 Start": 6,
#     "P1 Up": 7,
#     "Power": 8,
#     "Reset": 9
# }

class Memory:
    """Client for reading from and writing to Bizhawk memory"""

    def __init__(self, 
        # Memory domain
        domain: str,
        # Default arguments for all operations
        signed: int=False, size: int=1, endianness: str='big',
        # Address and port for socket connection
        address: str='127.0.0.1', port: int=16154
    ):
        self.domain = domain

        self.default_signed = signed
        self.default_size = size
        self.default_endianness = endianness
        
        self.address = address
        self.port = port


    def _request(self, query):

        # Socket requires a byte string to send
        if type(query) is not bytes:
            query = query.encode()

        print(query.decode('ascii'))

        with create_connection((self.address, self.port)) as socket:
            # Send request and expect response
            socket.sendall(query)
            response = self._receive(socket)


        try:
            # Extract response code and message
            code, _, message = response.decode('UTF-8').partition('_')
            code = int(code)
        
        except ValueError:
            raise InvalidResponse('Response could not be divided into code and message')


        # Successfully wrote to memory
        if code == 0:
            return True

        # Successfully read byte
        if code == 1:
            return response[response.index(b'_'):]

        # Successfully read integer
        if code == 2:
            return int(message)

        # Successfully read float
        if code == 3:
            return float(message)


        raise InvalidRequest(code, message)

    def _receive(self, socket: Socket, n: int=128):
        """Receive data until end of stream"""

        # Receive data in packets
        # and concatenate them at the end

        buffer = []

        while True:
            data = socket.recv(n)

            if not data:
                break

            buffer.append(data)

        return b''.join(buffer)

    def build_query(self, form, address=0x00):
        '''
        [input]
        0 /  button

        [read bytes]
        1 / domain / address

        '''

        if form == FORM['INPUT']:
            pass

        elif form == FORM['READ']:
            # form / domain / address
            query = str(form) + DELIMITER + str(self.domain) + DELIMITER + str(address)
            return query

        else:
            raise("Invalid argument type")

        return 

    def read_byte(self, address: int):
        """Read byte from memory"""
        q = self.build_query(address)
        return self._request(q)
