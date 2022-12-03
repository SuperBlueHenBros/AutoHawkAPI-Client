from socket import AF_INET, SOCK_STREAM, SHUT_RDWR
from socket import socket as Socket
from socket import create_connection

from .exceptions import InvalidRequest, InvalidResponse

'''
Planned:
client:
    load rom
    reset?
'''
QUERY_TYPE = {
    "INPUT": 0,
    "READ": 1,
    "WRITE": 2,
    "CLIENT": 3
}

CLIENT_TYPE = {
    "ADVANCE": 0,
    "SAVE": 1,
    "LOAD": 2,
}

RESPONSE_CODES = {
	"INPUT":    0,  # Successfully passed input
	"BYTE":     1,  # Successfully read byte
	"INTEGER":  2,  # Successfully read integer
	"CLIENT":    3,  # Successfully read float
	"ERROR":    4   # Generic error
}


DELIMITER = '/'


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
        # print("_request")

        # Socket requires a byte string to send
        if type(query) is not bytes:
            query = query.encode()

        # print("_request: query:", query.decode('ascii'))

        with create_connection((self.address, self.port)) as socket:
            # print("_request: sending")
            # Send request and expect response
            socket.sendall(query)
            response = self._receive(socket)

        try:
            # Extract response code and message
            code, _, message = response.decode('UTF-8').partition('_')
            if code == '':
                code = 4
            else:
                code = int(code)
            # print(f"_request: code={code} message={message}")
        
        except ValueError:
            raise InvalidResponse('Response could not be divided into code and message')


        # Successfully wrote to memory
        if code == RESPONSE_CODES["INPUT"]:
            return True

        # Successfully read byte
        if code == RESPONSE_CODES["BYTE"]:
            return response[response.index(b'_'):]

        # Successfully read integer
        if code == RESPONSE_CODES["INTEGER"]:
            return int(message)

        # Successfully modified client
        if code == RESPONSE_CODES["CLIENT"]:
            return True

        if code == RESPONSE_CODES["ERROR"]:
            return False


        raise InvalidRequest(code, message)

    def _receive(self, socket: Socket, n: int=128):
        """Receive data until end of stream"""

        # Receive data in packets
        # and concatenate them at the end

        buffer = []
        while True:
            try:
                data = socket.recv(n)
            except ConnectionResetError as e:
                print("ConnectionResetError:", e)
                break
            except ConnectionAbortedError as e:
                print("ConnectionAbortedError:", e)
                break

            if not data:
                # print("_receive: no data")
                break

            buffer.append(data)

        return b''.join(buffer)

    # TODO: get rid of this universal function implimentation and just make each query it's own function. 
    #       this format made more sense when all queries had the same basic arguments
    def build_query(self, query_type: int, address: int=0x00, button_name: str=None, 
                    button_state: bool=None, client_type: int=None, frames: int=None):
        '''
        QUERY FORMATS:

        [input]
        0 / button_name / button_state /

        [read bytes]
        1 / domain / address /

        [advance frame]
        3 / 0 / frames / 

        '''
        if query_type == QUERY_TYPE['INPUT']:
            # 0 / button_name / button_state /
            try:
                query = str(query_type) + DELIMITER + button_name + DELIMITER + str(button_state) + DELIMITER
                return query
            except TypeError as e:
                raise(f"Arguments missing from query...\n{e}")
            

        elif query_type == QUERY_TYPE['READ']:
            # 1 / domain / address /
            try:
                query = str(query_type) + DELIMITER + str(self.domain) + DELIMITER + str(address) + DELIMITER
                return query
            except TypeError as e:
                raise(f"Arguments missing from query...\n{e}")

        elif query_type == QUERY_TYPE['CLIENT']:
            if client_type == CLIENT_TYPE["ADVANCE"]:
                # 3 / 0 / frames /
                try:
                    query = str(query_type) + DELIMITER + str(client_type) + DELIMITER + str(frames) + DELIMITER
                    return query
                except TypeError as e:
                    raise(f"Arguments missing from query...\n{e}")

            elif client_type == CLIENT_TYPE["SAVE"]:
                # 3 / 1 / 
                try:
                    query = str(query_type) + DELIMITER + str(client_type) + DELIMITER
                    return query
                except TypeError as e:
                    raise(f"Arguments missing from query...\n{e}")

            
            elif client_type == CLIENT_TYPE["LOAD"]:
                # 3 / 2 / 
                try:
                    query = str(query_type) + DELIMITER + str(client_type) + DELIMITER
                    return query
                except TypeError as e:
                    raise(f"Arguments missing from query...\n{e}")
                
        else:
            raise("Invalid argument type")
            
        return 

    def read_byte(self, address: int):
        """Read byte from memory"""
        q = self.build_query(QUERY_TYPE["READ"], address=address)
        return self._request(q)

    def send_input(self, key_name: str, key_state: bool):
        """Pass input to emulator"""
        q = self.build_query(QUERY_TYPE["INPUT"], button_name=key_name, button_state=key_state)
        return self._request(q)

    def advance_frame(self, frames=1):
        """Tell emulator to advance frame"""
        q = self.build_query(QUERY_TYPE["CLIENT"], client_type=CLIENT_TYPE["ADVANCE"], frames=frames)
        return self._request(q)

    def save_state(self):
        q = self.build_query(QUERY_TYPE["CLIENT"], client_type=CLIENT_TYPE["SAVE"])
        return self._request(q)

    def load_state(self):
        q = self.build_query(QUERY_TYPE["CLIENT"], client_type=CLIENT_TYPE["LOAD"])
        return self._request(q)