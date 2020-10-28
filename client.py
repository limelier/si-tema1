import socket
from typing import Set
from socket_util import send_header, recv_header

host = '127.0.0.1'
port_A = 3002
port_B = 3003
port_K = 3001

shared_key = b'\x08\xe4\x7f\xe8\xf2-\x86l\xef\xca\x83\xf7\xa0?\xf2N\xd9\x98F\x01\xadkhG\x8d\xcc\x1f\x90\xc5H,\x98'


def get_choice(prompt: str, allowed_choices: Set[str]) -> str:
    choice = ''
    while not choice:
        choice = input(prompt + '\n').lower()
        if choice not in allowed_choices:
            print('Answer not in {}, please try again.'.format(allowed_choices))
            choice = ''
    return choice


def initiate():
    choice = get_choice('ECB or OFB?', {'ecb', 'ofb'})
    data = bytes()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port_K))
        send_header(s, bytes(choice, 'utf-8'))
        data = recv_header(s)
        s.sendall(b'doy')

    print(data)


def wait():
    pass


def main():
    choice = get_choice('[I]nitiate a conversation, or [w]ait for one?', {'i', 'w'})
    if choice == 'i':
        initiate()
    else:
        wait()


if __name__ == '__main__':
    main()
