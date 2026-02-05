# ecc_utils.py
from reedsolo import RSCodec

def add_ecc(data: bytes, nsym: int = 32) -> bytes:
    """
    Append Reed-Solomon parity symbols to `data`.
    nsym = number of parity bytes (tune per required correction strength).
    """
    rs = RSCodec(nsym)
    return rs.encode(data)

def decode_ecc(encoded: bytes, nsym: int = 32) -> bytes:
    """
    Decode and correct Reed-Solomon encoded bytes. Returns corrected original bytes.
    May raise reedsolo.ReedSolomonError if unrecoverable.
    """
    rs = RSCodec(nsym)
    decoded = rs.decode(encoded)
    # reedsolo sometimes returns tuple (msg, ecc) depending on version — normalize:
    if isinstance(decoded, tuple):
        return decoded[0]
    return decoded
