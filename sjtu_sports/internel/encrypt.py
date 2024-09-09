from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Util.Padding import pad
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from random import choice


def aes_encrypt(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    data = data.encode()
    data = pad(data, AES.block_size)
    return b64encode(cipher.encrypt(data)).decode()


def aes_decrypt(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(b64decode(data)).decode('utf-8').rstrip('\x06')


def rsa_encrypt(pubkey, data):
    cipher = PKCS1_v1_5.new(RSA.import_key(pubkey))
    c = cipher.encrypt(data.encode())
    return b64encode(c).decode()

