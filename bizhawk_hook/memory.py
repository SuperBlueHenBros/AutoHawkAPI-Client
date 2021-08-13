from socket import AF_INET, SOCK_STREAM, SHUT_RDWR
from socket import socket as Socket

from typing import Union

from .exceptions import InvalidRequest



class Memory:
    """Client for reading from and writing to Bizhawk memory"""

    def __init__(self, address: str = '127.0.0.1', port: int = 16154):
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

        # Set up and connect to socket
    
        # (This uses a new connection every time for convenience
        # on the client end. The difference between a temporary
        # and a maintained connection should be negligable.)

        socket = Socket(AF_INET, SOCK_STREAM)
        socket.connect((self.address, self.port))

        # Make sure query is a byte string
        if type(query) is not bytes:
            query = query.encode()

        # Send request and expect response
        socket.sendall(query)
        response = self._receive(socket)

        # Close connection
        socket.shutdown(SHUT_RDWR)
        socket.close()

        # Extract response code and message
        code, _, message = response.partition('_')
        code = int(code)

        # Anything but 0 is an error message
        if code != 0:
            raise InvalidRequest(code, message)

        return message

    def _receive(self, socket: Socket, n: int = 128):
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