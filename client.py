import os
import socket
from typing import Set

from crypt import CipherECB, CipherOFB
from socket_util import send_header, recv_header

host = '127.0.0.1'
port_A = 3002
port_B = 3003
port_KM = 3001

shared_key = b'\x08\xe4\x7f\xe8\xf2-\x86l\xef\xca\x83\xf7\xa0?\xf2N\xd9\x98F\x01\xadkhG\x8d\xcc\x1f\x90\xc5H,\x98'
shared_cipher = CipherECB(shared_key)


def get_choice(prompt: str, allowed_choices: Set[str]) -> str:
    choice = ''
    while not choice:
        choice = input(prompt + '\n').lower()
        if choice not in allowed_choices:
            print('Answer not in {}, please try again.'.format(allowed_choices))
            choice = ''
    return choice


def get_conversation_key(choice: bytes):
    data: bytes
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port_KM))
        send_header(s, choice)
        data = recv_header(s)
    conversation_key = shared_cipher.decrypt(data)
    return conversation_key


def initiate():
    print('Make sure the other party is waiting.')
    choice = get_choice('ECB or OFB?', {'ecb', 'ofb'})
    print('Getting encryption key...')
    key = get_conversation_key(bytes(choice, 'utf-8'))
    print('Got {} encryption key.'.format(choice.upper()))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port_B))
            send_header(s, bytes(choice, 'utf-8'))

            if choice == 'ecb':
                cipher = CipherECB(key)
                message = input('What would you like to send?\n')
                send_header(s, cipher.encrypt(bytes(message, 'utf-8')))
                print('Great! Waiting for reply...')
                reply = cipher.decrypt(recv_header(s))
            else:
                send_iv, receive_iv = os.urandom(16), os.urandom(16)
                send_header(s, send_iv)
                send_header(s, receive_iv)
                cipher_send = CipherOFB(key, send_iv)
                cipher_recv = CipherOFB(key, receive_iv)
                message = input('What would you like to send?\n')
                send_header(s, cipher_send.transform(bytes(message, 'utf-8')))
                print('Message sent, waiting for reply.')
                reply = cipher_recv.transform(recv_header(s))
        print('Reply received:')
        print('>', str(reply, 'utf-8'))
    except ConnectionRefusedError:
        print("Sorry, looks like nobody's waiting for a conversation.")


def wait():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port_B))
        s.listen()
        print('Waiting for a connection...')
        conn, _ = s.accept()
    print('Got a connection!')
    with conn:
        print('Conversation initiating...')
        choice = recv_header(conn)
        print('Peer is using {} encryption, fetching key...'.format(choice.upper()))
        key = get_conversation_key(choice)
        print('Got key, awaiting message...')

        if choice == b'ecb':
            cipher = CipherECB(key)
            message = cipher.decrypt(recv_header(conn))
            print('Message received!')
            print('>', str(message, 'utf-8'))
            reply = input('Type a reply:\n')
            send_header(conn, cipher.encrypt(bytes(reply, 'utf-8')))
        elif choice == b'ofb':
            receive_iv = recv_header(conn)
            send_iv = recv_header(conn)
            receive_cipher = CipherOFB(key, receive_iv)
            send_cipher = CipherOFB(key, send_iv)
            message = receive_cipher.transform(recv_header(conn))
            print('Message received!')
            print('>', str(message, 'utf-8'))
            reply = input('Type a reply:\n')
            send_header(conn, send_cipher.transform(bytes(reply, 'utf-8')))
        else:
            print('Encryption format unknown, shutting down.')
            exit(1)
        print('Reply sent.')


def main():
    choice = get_choice('[I]nitiate a conversation, or [w]ait for one?', {'i', 'w'})
    if choice == 'i':
        initiate()
    else:
        wait()


if __name__ == '__main__':
    main()
