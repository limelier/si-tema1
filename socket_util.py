# Socket utilities module
from socket import socket

HEADER_SIZE = 4  # bytes


class SocketEOFException(Exception):
    def __init__(self):
        super().__init__('Socket EOF reached while awaiting read.')


def send_header(s: socket, buffer: bytes):
    header: int = len(buffer)
    s.sendall(header.to_bytes(HEADER_SIZE, byteorder='big'))
    s.sendall(buffer)


def recv_fixed(s: socket, count: int) -> bytes:
    buffer = bytes()
    while len(buffer) < count:
        partial = s.recv(count - len(buffer))
        if len(partial) == 0:
            raise SocketEOFException()
        buffer += partial
    return buffer


def recv_header(s: socket) -> bytes:
    count = int.from_bytes(recv_fixed(s, HEADER_SIZE), byteorder='big')
    return recv_fixed(s, count)
