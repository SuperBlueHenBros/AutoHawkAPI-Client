from socket import AF_INET, SOCK_STREAM, SHUT_RDWR
from socket import socket as Socket
from socket import create_connection

from typing import Union

from .exceptions import InvalidRequest, InvalidResponse



class Memory:
    """Client for reading from and writing to Bizhawk memory"""

    def __init__(self, domain: str, address: str='127.0.0.1', port: int=16154):
        self.domain = domain
        
        self.address = address
        self.port = port


    def _request(self, query: Union[bytes, str]):
        """Send a request to the Bizhawk Lua memory hook


        Pattern:  DOMN/ADDR/TSLE/VLUE

        DOMN  - Memory domain
        ADDR  - Address
        TSLE--.-------------------.
            Type:               Signage:
            | * [b]yte            * [u]nsigned
            | * [i]nteger         * [s]igned
            | * [f]loat
            |
            .-------------------.
            Length              Endianness
                * [1] byte          * [l]ittle endian
                * [2] bytes         * [b]ig endian
                * [3] bytes
                * [4] bytes

        VLUE  - Integer or float, ex. 12 or -1.2
        

        # EXAMPLES

        VRAM/11423051/iu4b/23
            Write (23) to (11423051) in (VRAM)
            an [i]nteger, [u]nsigned,
            [4] bytes long and [b]ig endian

        WRAM/21512962/fs2l/
            Read from (21512962) in (WRAM)
            a [f]loat, [s]igned,
            [2] bytes long and [l]ittle endian
        """

        # Socket requires a byte string to send
        if type(query) is not bytes:
            query = query.encode()


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

    def _format_tsle(self, type_: type, signed: bool, length: int, endianness: str):
        """Format the type, signage, length, and endianness for a request"""

        if type_ not in (bytes, int, float):
            raise ValueError('Type must be bytes, int or float')

        if length not in (1, 2, 3, 4):
            raise ValueError('Length must be 1, 2, 3 or 4 bytes')

        if endianness not in ('little', 'big'):
            raise ValueError('Endianness must be little or big')


        return ''.join([
            type_.__name__[0],
            'us'[signed],
            str(length),
            endianness[0]
        ])
    
    def _format_query(self, address: int, type_: type=bytes, signed: bool=False,
                        length: int=1, endianness: str='big', value: Union[int, float]=None):
        """Format all request parameters into a valid query for a request"""

        tsle = self._format_tsle(type_, signed, length, endianness)            
        return f'{self.domain}/{address}/{tsle}/{"" if value is None else value}'


    def read_byte(self, address: int):
        """Read byte from memory"""
        return self._request(self._format_query(
            address=address,
            type_=bytes,
            value=None
        ))

    def write_byte(self, address: int, value: int):
        """Write byte from memory"""
        return self._request(self._format_query(
            address=address,
            type_=bytes,
            value=value
        ))

    def read_int(self, address: int, signed: bool=False, length: int=1, endianness: str='big'):
        """Read integer from memory"""
        return self._request(self._format_query(
            address=address,
            type_=int,
            signed=signed,
            length=length,
            endianness=endianness,
            value=None
        ))

    def write_int(self, address: int, value: int, signed: bool=False, length: int=1, endianness: str='big'):
        """Write integer from memory"""
        return self._request(self._format_query(
            address=address,
            type_=int,
            signed=signed,
            length=length,
            endianness=endianness,
            value=value
        ))

    def read_float(self, address: int, endianness: str='big'):
        """Read float from memory"""
        return self._request(self._format_query(
            address=address,
            type_=float,
            endianness=endianness,
            value=None
        ))

    def write_float(self, address: int, value: int, endianness: str='big'):
        """Write float from memory"""
        return self._request(self._format_query(
            address=address,
            type_=float,
            endianness=endianness,
            value=value
        ))