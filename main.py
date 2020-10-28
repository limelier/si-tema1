import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


key = os.urandom(32)
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()

plaintext = 'hello, world'.rjust(32, ' ')
ciphertext = encryptor.update(bytes(plaintext, 'utf-8')) + encryptor.finalize()
decryptor = cipher.decryptor()
decrypted = decryptor.update(ciphertext) + decryptor.finalize()

print(decrypted.decode('utf-8').lstrip())
