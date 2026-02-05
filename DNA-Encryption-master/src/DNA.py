# ===============================
# DNA.py  — Hybrid Digital + Physical DNA Encryption
# ===============================
import os
import base64
from utils import *
import adaptiveHuffman
from aes_dna import (
    derive_aes_key_from_dna_file,
    encrypt_bytes,
    decrypt_bytes,
    bytes_to_bitstring,
    bitstring_to_bytes,
    nonce_to_b64,
)
from ecc import ecc_encode, ecc_decode

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KEY_PATH = os.path.join(BASE_DIR, "key", "Key.txt")
CIPHER_PATH = os.path.join(BASE_DIR, "cipher", "Cipher.txt")
DECRYPT_PATH = os.path.join(BASE_DIR, "decrypted")
DNA_KEY_PATH = os.path.join(BASE_DIR, "dna_sequence.txt")  # physical DNA-based key file

# Ensure directories exist
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CIPHER_PATH), exist_ok=True)
os.makedirs(DECRYPT_PATH, exist_ok=True)

# 2-bit → base mapping
TABLE = {"00": "A", "01": "G", "10": "C", "11": "T"}


def Encode(bitstring: str):
    """
    Encode bitstring to DNA sequence with constraints:
    - Avoid ≥4 same bases (homopolymers)
    - Maintain GC% balance
    """
    dna = []
    for i in range(0, len(bitstring), 2):
        pair = bitstring[i:i+2]
        base = TABLE.get(pair, "A")

        # Prevent long homopolymers
        if len(dna) >= 3 and dna[-1] == dna[-2] == dna[-3] == base:
            base = random.choice([b for b in "AGCT" if b != base])
        dna.append(base)
    return dna


def FileEncryption(path):
    """
    Complete encryption pipeline:
    Compress -> AES-GCM encrypt -> ECC -> DNA encode -> Save cipher + metadata
    """
    print("Compressing using Adaptive Huffman...")
    Compressor = adaptiveHuffman.AdaptiveHuffman()
    Compressor.compress(path, "Compression.txt")

    with open("Compression.txt", "rb") as f:
        compressed_bytes = f.read()

    if not os.path.isfile(DNA_KEY_PATH):
        raise FileNotFoundError(
            f"DNA key file not found: {DNA_KEY_PATH}\nCreate it with your DNA key sequence."
        )

    print("Deriving AES key from physical DNA file...")
    aes_key = derive_aes_key_from_dna_file(DNA_KEY_PATH, key_bytes=32)

    print("Encrypting with AES-GCM...")
    aes_out = encrypt_bytes(compressed_bytes, aes_key)
    nonce = aes_out["nonce"]
    ciphertext_bytes = aes_out["ciphertext"]

    print("Adding Reed–Solomon ECC...")
    ecc_bytes = ecc_encode(ciphertext_bytes)

    print("Encoding bytes into DNA bases...")
    bitstr = bytes_to_bitstring(ecc_bytes)
    dna_seq = "".join(Encode(bitstr))

    print("Saving Cipher and Metadata...")
    with open(CIPHER_PATH, "w") as cf:
        cf.write(dna_seq)

    with open(KEY_PATH, "w") as kf:
        kf.write("algorithm:AES-GCM-256\n")
        kf.write(f"dna_file:{os.path.relpath(DNA_KEY_PATH, BASE_DIR)}\n")
        kf.write(f"nonce_b64:{nonce_to_b64(nonce)}\n")

    # cleanup
    try:
        os.remove("Compression.txt")
    except Exception:
        pass

    print(f"\nEncryption complete ✅\nCipher saved: {CIPHER_PATH}\nMetadata saved: {KEY_PATH}\n")


def TextEncryption():
    """
    Take user input and run full encryption pipeline.
    """
    text = input("Enter your message to encrypt: ")
    with open("InputText.txt", "w", encoding="utf-8") as f:
        f.write(text)
    FileEncryption("InputText.txt")
    try:
        os.remove("InputText.txt")
    except Exception:
        pass


def Decode(ciphertext: str, key_meta: dict, out_type: str):
    """
    Decode DNA -> ECC decode -> AES decrypt -> Decompress
    """
    print("Decoding DNA sequence to bits...")
    # DNA → bitstring
    bitstr = "".join(
        list(TABLE.keys())[list(TABLE.values()).index(base)]
        for base in ciphertext
        if base in TABLE.values()
    )

    cipher_bytes = bitstring_to_bytes(bitstr)

    print("Applying ECC correction...")
    ecc_corrected = ecc_decode(cipher_bytes)

    dna_file = key_meta.get("dna_file", DNA_KEY_PATH)
    if not os.path.isabs(dna_file):
        dna_file = os.path.join(BASE_DIR, dna_file)

    aes_key = derive_aes_key_from_dna_file(dna_file, key_bytes=32)

    print("Decrypting AES-GCM ciphertext...")
    nonce = key_meta["nonce_bytes"]
    compressed_bytes = decrypt_bytes(ecc_corrected, nonce, aes_key)

    print("Decompressing using Adaptive Huffman...")
    bitstream = "".join(f"{byte:08b}" for byte in compressed_bytes)

    if out_type == "text":
        output_file = os.path.join(DECRYPT_PATH, "PlainTextResult.txt")
    elif out_type == "image":
        output_file = os.path.join(DECRYPT_PATH, "DecodedImage.png")
    else:
        raise ValueError("Unknown out_type: " + str(out_type))

    adaptiveHuffman.AdaptiveHuffman().expand(bitstream, output_file)
    print(f"Decryption complete ✅\nOutput file: {output_file}\n")


def Decryption(ciphertext_path, key_path, type):
    """
    Perform full decryption: DNA -> ECC correction -> AES-GCM -> Decompression
    """
    print("Starting Decryption Pipeline...\n")
    if not os.path.isfile(ciphertext_path):
        raise FileNotFoundError(f"Cipher not found: {ciphertext_path}")
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"Key/meta not found: {key_path}")

    with open(ciphertext_path, "r") as cf:
        ciphertexts = cf.read().strip()

    meta_raw = open(key_path, "r").read().splitlines()
    key_meta = {}
    for line in meta_raw:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "nonce_b64":
            key_meta["nonce_bytes"] = base64.b64decode(v)
        elif k == "dna_file":
            key_meta["dna_file"] = v
        else:
            key_meta[k] = v

    if "nonce_bytes" not in key_meta:
        raise RuntimeError("Metadata (nonce) missing in key file.")

    Decode(ciphertexts, key_meta, type)
