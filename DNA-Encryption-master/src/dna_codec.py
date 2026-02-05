# dna_codec.py
"""
Simple invertible bytes <-> DNA coder.
This uses a deterministic 2-bit -> base mapping (00->A,01->C,10->G,11->T)
and includes small helper checks for homopolymers and GC.
For production synthesis use, replace with enumerative constrained coding.
"""

BASE_MAP = {
    '00': 'A',
    '01': 'C',
    '10': 'G',
    '11': 'T'
}
REV_MAP = {v: k for k, v in BASE_MAP.items()}

def bytes_to_dna(b: bytes) -> str:
    bitstr = ''.join(f'{byte:08b}' for byte in b)
    if len(bitstr) % 2:
        bitstr += '0'  # pad one bit if needed
    dna = ''.join(BASE_MAP[bitstr[i:i+2]] for i in range(0, len(bitstr), 2))
    return dna

def dna_to_bytes(dna: str) -> bytes:
    bitstr = ''.join(REV_MAP[c] for c in dna)
    # drop padding bits at the end if they were added (decoder should know original length via metadata)
    pad = (-len(bitstr)) % 8
    if pad:
        # if padded when encoding, the encoder should record original length; here we just truncate
        bitstr = bitstr[:-pad]
    return bytes(int(bitstr[i:i+8], 2) for i in range(0, len(bitstr), 8))

def has_long_homopolymer(dna: str, max_run: int = 3) -> bool:
    run = 1
    for i in range(1, len(dna)):
        if dna[i] == dna[i-1]:
            run += 1
            if run > max_run:
                return True
        else:
            run = 1
    return False

def gc_content(dna: str) -> float:
    if not dna:
        return 0.0
    gc = dna.count('G') + dna.count('C')
    return gc / len(dna)
