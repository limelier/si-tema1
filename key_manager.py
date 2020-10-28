import os
import socket
from typing import Any

from socket_util import send_header, recv_header

ecb_key = os.urandom(32)
ofb_key = os.urandom(32)

host = '127.0.0.1'  # localhost
port = 3001

shared_key = b'\x08\xe4\x7f\xe8\xf2-\x86l\xef\xca\x83\xf7\xa0?\xf2N\xd9\x98F\x01\xadkhG\x8d\xcc\x1f\x90\xc5H,\x98'


def handle(client_socket: socket, addr: Any):
    with client_socket:
        print('Connection from', addr)
        data = recv_header(client_socket)
        print('Received ', data)
        if data == b'ecb':
            send_header(client_socket, ecb_key)
        elif data == b'ofb':
            send_header(client_socket, ofb_key)
        else:
            send_header(client_socket, b'wait, what?')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        while True:
            s.listen()
            print('Listening on port 3001...')
            conn, addr = s.accept()
            handle(conn, addr)


if __name__ == '__main__':
    main()


