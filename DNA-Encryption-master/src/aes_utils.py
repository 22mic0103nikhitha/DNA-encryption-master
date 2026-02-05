# aes_utils.py
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def aes_encrypt(plaintext):
    # Handle tuple or non-byte inputs
    if isinstance(plaintext, tuple):
        plaintext = plaintext[0]
    if not isinstance(plaintext, (bytes, bytearray)):
        plaintext = str(plaintext).encode()

    key = os.urandom(32)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct_and_tag = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    ciphertext = ct_and_tag[:-16]
    tag = ct_and_tag[-16:]
    return ciphertext, key, nonce, tag

def aes_decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes):
    """
    Decrypt using AES-GCM given ciphertext, key, nonce, tag.
    Returns plaintext bytes or raises if verification fails.
    """
    aesgcm = AESGCM(key)
    ct_and_tag = ciphertext + tag
    plaintext = aesgcm.decrypt(nonce, ct_and_tag, associated_data=None)
    return plaintext
