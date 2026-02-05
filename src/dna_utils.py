# dna_utils.py
"""
Simple deterministic bytes <-> DNA mapping.

Mapping:
  00 -> A
  01 -> C
  10 -> G
  11 -> T

This codec is invertible and fast. For synthesis-grade constraints
you can swap to the more advanced encoder/packer in previous messages.
"""

BASE_MAP = {
    '00': 'A',
    '01': 'C',
    '10': 'G',
    '11': 'T'
}
REV_MAP = {v: k for k, v in BASE_MAP.items()}

def bytes_to_dna(b: bytes) -> str:
    """Convert bytes -> dna string (A/C/G/T)."""
    bitstr = ''.join(f'{byte:08b}' for byte in b)
    if len(bitstr) % 2:
        bitstr += '0'
    dna = ''.join(BASE_MAP[bitstr[i:i+2]] for i in range(0, len(bitstr), 2))
    return dna

def dna_to_bytes(dna: str) -> bytes:
    """Convert dna string (A/C/G/T) -> bytes."""
    bitstr = ''.join(REV_MAP[c] for c in dna.strip() if c in REV_MAP)
    # if padded, truncate to whole bytes
    if len(bitstr) % 8 != 0:
        bitstr = bitstr[: (len(bitstr) // 8) * 8 ]
    out = bytes(int(bitstr[i:i+8], 2) for i in range(0, len(bitstr), 8))
    return out
