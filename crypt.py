import os
from typing import List

from Crypto.Cipher import AES


def null_pad(byte_str: bytes, block_size: int) -> bytes:
    padding_len = block_size - (len(byte_str) % block_size)

    if padding_len == block_size:
        return byte_str
    else:
        padding = padding_len * b'\0'
        return byte_str + padding


def null_unpad(padded_str: bytes) -> bytes:
    padding_len = 0
    while padded_str[-(1 + padding_len)] == 0x00:
        padding_len += 1

    if padding_len == 0:
        return padded_str
    else:
        return padded_str[:-padding_len]


def split_blocks(byte_str: bytes, block_size: int) -> List[bytes]:
    return [
        byte_str[i:i+block_size]
        for i in range(0, len(byte_str), block_size)
    ]


def encrypt_ecb(key: bytes, plaintext: bytes) -> bytes:
    plaintext = null_pad(plaintext, 16)
    cipher = AES.new(key, AES.MODE_ECB)
    plain_blocks = split_blocks(plaintext, 16)
    enc_blocks = [cipher.encrypt(block) for block in plain_blocks]
    encrypted = b''.join(enc_blocks)
    return encrypted


def decrypt_ecb(key: bytes, ciphertext: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_blocks = split_blocks(ciphertext, 16)
    dec_blocks = [cipher.decrypt(block) for block in cipher_blocks]
    decrypted = b''.join(dec_blocks)
    decrypted = null_unpad(decrypted)
    return decrypted


def keystream_blocks(key: bytes, iv: bytes, count: int) -> List[bytes]:
    cipher = AES.new(key, AES.MODE_ECB)
    blocks = [cipher.encrypt(iv)]

    for i in range(1, count):
        blocks += cipher.encrypt(blocks[-1])

    return blocks


def xor_block(first: bytes, second: bytes) -> bytes:
    return bytes(pair[0] ^ pair[1] for pair in zip(first, second))


def encrypt_ofb(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    plaintext = null_pad(plaintext, 16)
    plain_blocks = split_blocks(plaintext, 16)
    xor_blocks = keystream_blocks(key, iv, len(plain_blocks))
    enc_blocks = [
        xor_block(pair[0], pair[1])
        for pair in zip(plain_blocks, xor_blocks)
    ]
    encrypted = b''.join(enc_blocks)
    return encrypted


def decrypt_ofb(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    plain_blocks = split_blocks(ciphertext, 16)
    xor_blocks = keystream_blocks(key, iv, len(plain_blocks))
    dec_blocks = [
        xor_block(pair[0], pair[1])
        for pair in zip(plain_blocks, xor_blocks)
    ]
    decrypted = b''.join(dec_blocks)
    decrypted = null_unpad(decrypted)
    return decrypted


def testing():
    key = os.urandom(16)
    enc = encrypt_ofb(key, b'0'*16, b'hello world')
    dec = decrypt_ofb(key, b'0'*16, enc)
    print(dec)


if __name__ == '__main__':
    testing()

