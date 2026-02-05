# ===============================
# ecc.py  —  Reed–Solomon / Fallback Error Correction
# ===============================
import os
import hashlib

try:
    import reedsolo
    _USE_RS = True
except ImportError:
    _USE_RS = False
    print("[ecc.py] Warning: 'reedsolo' not found. Using fallback ECC (simple redundancy).")


# ===============================
# Reed–Solomon ECC encode/decode
# ===============================
def ecc_encode(data: bytes, nsym: int = 16) -> bytes:
    """
    Apply ECC redundancy to the ciphertext bytes.
    If reedsolo is available: uses proper RS encoding.
    Otherwise, appends SHA256 checksum for integrity.
    """
    if _USE_RS:
        rs = reedsolo.RSCodec(nsym)
        encoded = rs.encode(data)
        return encoded
    else:
        checksum = hashlib.sha256(data).digest()
        return data + checksum


def ecc_decode(encoded: bytes, nsym: int = 16) -> bytes:
    """
    Decode and verify ECC-corrected data.
    If RS available, attempts to fix errors.
    Fallback verifies checksum integrity.
    """
    if _USE_RS:
        rs = reedsolo.RSCodec(nsym)
        try:
            decoded = rs.decode(encoded)[0]  # returns (data, ecc)
            return decoded
        except reedsolo.ReedSolomonError as e:
            print(f"[ecc.py] Reed–Solomon failed to fully correct: {e}")
            raise
    else:
        if len(encoded) < 32:
            raise ValueError("Encoded data too short to contain checksum.")
        data, checksum = encoded[:-32], encoded[-32:]
        if hashlib.sha256(data).digest() != checksum:
            raise ValueError("[ecc.py] ECC checksum verification failed.")
        return data


# ===============================
# Optional noise simulation
# ===============================
def introduce_noise(data: bytes, num_flips: int = 2) -> bytes:
    """
    Simulate random bit errors (for testing ECC correction).
    Useful for validating DNA decoding robustness.
    """
    import random

    if len(data) == 0:
        return data

    bytearray_data = bytearray(data)
    for _ in range(num_flips):
        i = random.randint(0, len(bytearray_data) - 1)
        bit = 1 << random.randint(0, 7)
        bytearray_data[i] ^= bit
    return bytes(bytearray_data)
