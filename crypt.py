import os
from typing import List

from Crypto.Cipher import AES


class CipherECB:
    def __init__(self, key: bytes):
        self._key: bytes = key
        self._cipher: AES = AES.new(key, AES.MODE_ECB)

    @staticmethod
    def _null_pad(byte_str: bytes, block_size: int) -> bytes:
        padding_len = block_size - (len(byte_str) % block_size)

        if padding_len == block_size:
            return byte_str
        else:
            padding = padding_len * b'\0'
            return byte_str + padding

    @staticmethod
    def _null_unpad(padded_str: bytes) -> bytes:
        padding_len = 0
        while padded_str[-(1 + padding_len)] == 0x00:
            padding_len += 1

        if padding_len == 0:
            return padded_str
        else:
            return padded_str[:-padding_len]

    @staticmethod
    def _split_blocks(byte_str: bytes, block_size: int) -> List[bytes]:
        return [
            byte_str[i:i + block_size]
            for i in range(0, len(byte_str), block_size)
        ]

    def encrypt(self, plaintext: bytes) -> bytes:
        plaintext = self._null_pad(plaintext, 16)
        plain_blocks = self._split_blocks(plaintext, 16)
        enc_blocks = [self._cipher.encrypt(block) for block in plain_blocks]
        encrypted = b''.join(enc_blocks)
        return encrypted

    def decrypt(self, ciphertext: bytes) -> bytes:
        cipher_blocks = self._split_blocks(ciphertext, 16)
        dec_blocks = [self._cipher.decrypt(block) for block in cipher_blocks]
        decrypted = b''.join(dec_blocks)
        decrypted = self._null_unpad(decrypted)
        return decrypted


class CipherOFB:
    def __init__(self, key: bytes, iv: bytes):
        """
        Initialize with a 128-, 256- or 512-bit key, and a 16-byte initialization vector.
        """
        self._key: bytes = key
        self._iv: bytes = iv
        self._cipher: AES = AES.new(key, AES.MODE_ECB)
        self._keystream_block: bytes = self._cipher.encrypt(iv)

    def _gen_next_keystream_block(self):
        self._keystream_block = self._cipher.encrypt(self._keystream_block)

    def transform(self, input_text: bytes) -> bytes:
        """
        Encrypt OR decrypt the input text. DO NOT USE the same cipher for both functions.
        """
        ciphertext = bytearray(len(input_text))  # preallocate, same length as input_text
        i = 0
        for index, byte in enumerate(input_text):
            if i > 15:
                i = 0
                self._gen_next_keystream_block()
            ciphertext[index] = byte ^ self._keystream_block[i]
            i += 1
        return bytes(ciphertext)


def testing():
    key = os.urandom(16)

    # ecb
    cipher = CipherECB(key)
    enc = cipher.encrypt(b'hello, world!')
    dec = cipher.decrypt(enc)
    print(dec)

    # ofb
    encryptor = CipherOFB(key, b'0' * 16)
    enc = encryptor.transform(b'hello, world!')
    decryptor = CipherOFB(key, b'0' * 16)
    dec = decryptor.transform(enc)
    print(dec)


if __name__ == '__main__':
    testing()
