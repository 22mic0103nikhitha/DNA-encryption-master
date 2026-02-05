# ecc_rs.py
from reedsolo import RSCodec

def rs_encode(block: bytes, nsym: int = 32) -> bytes:
    """Return block with Reed-Solomon parity bytes appended."""
    rsc = RSCodec(nsym)
    return rsc.encode(block)

def rs_decode(encoded: bytes, nsym: int = 32) -> bytes:
    """Decode Reed-Solomon encoded bytes and return original bytes.
    Raises ReedSolomonError if unrecoverable.
    """
    rsc = RSCodec(nsym)
    decoded = rsc.decode(encoded)
    # reedsolo.decode may return a tuple on some versions
    if isinstance(decoded, tuple):
        return decoded[0]
    return decoded
