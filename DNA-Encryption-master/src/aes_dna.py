# aes_dna.py
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# DNA-bit mappings
_DNA_TO_BITS = {"A": "00", "G": "01", "C": "10", "T": "11"}
_BITS_TO_DNA = {v: k for k, v in _DNA_TO_BITS.items()}


def dna_to_bitstring(dna_seq: str) -> str:
    """Convert DNA sequence (A, G, C, T) into a bit string."""
    return "".join(_DNA_TO_BITS[c] for c in dna_seq.strip().upper() if c in _DNA_TO_BITS)


def bitstring_to_bytes(bitstr: str) -> bytes:
    """Convert bit string to bytes."""
    pad = (-len(bitstr)) % 8
    if pad:
        bitstr += "0" * pad
    return bytes(int(bitstr[i:i+8], 2) for i in range(0, len(bitstr), 8))


def bytes_to_bitstring(b: bytes) -> str:
    """Convert bytes to bit string."""
    return "".join(f"{byte:08b}" for byte in b)


def derive_aes_key_from_dna_file(dna_file_path: str, key_bytes: int = 32) -> bytes:
    """
    Derive AES key (default 256-bit) from a physical DNA sequence file.
    The DNA file contains ACTG characters; it’s hashed using SHA-256 to produce the key.
    """
    if not os.path.isfile(dna_file_path):
        raise FileNotFoundError(f"DNA file not found: {dna_file_path}")
    dna = open(dna_file_path, "r").read().strip().upper()
    bitstr = dna_to_bitstring(dna)
    digest = hashlib.sha256(bitstr.encode()).digest()
    return digest[:key_bytes]  # AES-256


def encrypt_bytes(plaintext: bytes, key: bytes) -> dict:
    """
    AES-GCM encrypt plaintext bytes with given key.
    Returns dict: {'nonce': bytes, 'ciphertext': bytes}
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # proper 96-bit nonce for AES-GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return {"nonce": nonce, "ciphertext": ciphertext}


def decrypt_bytes(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
    """AES-GCM decrypt ciphertext bytes with given key and nonce."""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def nonce_to_b64(nonce: bytes) -> str:
    return base64.b64encode(nonce).decode()


def nonce_from_b64(s: str) -> bytes:
    return base64.b64decode(s)
