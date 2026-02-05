# oligo_packer.py
import os
import json
import hashlib
from ecc_rs import rs_encode, rs_decode
from dna_codec import bytes_to_dna, dna_to_bytes, has_long_homopolymer, gc_content

def checksum16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:8]

def pack_into_oligos(ciphertext_bytes: bytes, oligo_data_size_bytes: int = 60, nsym: int = 20,
                     max_run: int = 3, gc_low: float = 0.40, gc_high: float = 0.60,
                     max_attempts: int = 5):
    """
    Chunk ciphertext_bytes into blocks, RS-encode each block (nsym parity),
    create DNA for each block, check constraints and attempt small tweaks if needed.
    Returns a list of oligo dicts: {"id":i,"dna":..., "meta":{...}}
    """
    total = len(ciphertext_bytes)
    chunks = [ciphertext_bytes[i:i+oligo_data_size_bytes] for i in range(0, total, oligo_data_size_bytes)]
    oligos = []
    for i, chunk in enumerate(chunks):
        attempt = 0
        success = False
        last_exception = None
        # we attempt to encode and satisfy constraints
        while attempt < max_attempts and not success:
            # optionally vary a tiny tweak: XOR first byte with attempt value to change bits deterministically
            if attempt == 0:
                block = chunk
                tweak = None
            else:
                # create a small tweak but keep reversible: store tweak byte in meta
                tweak = attempt & 0xFF
                block = bytes([chunk[0] ^ tweak]) + chunk[1:]
            try:
                encoded = rs_encode(block, nsym=nsym)
                dna = bytes_to_dna(encoded)
                # check constraints
                if has_long_homopolymer(dna, max_run=max_run) or not (gc_low <= gc_content(dna) <= gc_high):
                    attempt += 1
                    continue
                meta = {
                    "chunk_index": i,
                    "orig_len": len(chunk),
                    "rs_nsym": nsym,
                    "checksum": checksum16(encoded),
                    "tweak": tweak
                }
                oligos.append({"id": i, "dna": dna, "meta": meta})
                success = True
            except Exception as e:
                last_exception = e
                attempt += 1
        if not success:
            # as fallback accept the last encoded dna even if constraints fail (but record attempted tweak)
            encoded = rs_encode(chunk, nsym=nsym)
            dna = bytes_to_dna(encoded)
            meta = {
                "chunk_index": i,
                "orig_len": len(chunk),
                "rs_nsym": nsym,
                "checksum": checksum16(encoded),
                "tweak": None
            }
            oligos.append({"id": i, "dna": dna, "meta": meta})
    return oligos

def save_manifest(oligos, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(oligos, f, indent=2)

def load_manifest(path):
    with open(path, "r") as f:
        return json.load(f)

def unpack_oligos(oligo_list):
    """
    oligo_list: list of dicts {"id":..., "dna":..., "meta":{...}}
    returns concatenated ciphertext bytes (original chunks)
    """
    parts = []
    for o in sorted(oligo_list, key=lambda x: x["id"]):
        encoded = dna_to_bytes(o["dna"])
        # if a tweak was applied, reverse it after RS decode
        decoded = rs_decode(encoded, nsym=o["meta"]["rs_nsym"])
        orig_len = o["meta"]["orig_len"]
        if o["meta"].get("tweak") is not None:
            tweak = o["meta"]["tweak"]
            # reverse tweak applied earlier
            if len(decoded) > 0:
                decoded = bytes([decoded[0] ^ (tweak & 0xFF)]) + decoded[1:]
        # trim to original length
        parts.append(decoded[:orig_len])
    return b"".join(parts)
