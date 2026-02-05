# utils.py
import os
import random

# =============================
# === PATH CONFIGURATIONS ===
# =============================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

KEY_PATH = os.path.join(BASE_DIR, "key", "Key.txt")
CIPHER_PATH = os.path.join(BASE_DIR, "cipher", "Cipher.txt")
DECRYPT_PATH = os.path.join(BASE_DIR, "decrypted")

# Auto-create directories if not present
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CIPHER_PATH), exist_ok=True)
os.makedirs(DECRYPT_PATH, exist_ok=True)

# =============================
# === LEGACY LFSR FUNCTIONS ===
# (still available if you want to combine
#  physical DNA with dynamic pseudo-key streams)
# =============================

def keyXor(keys, text):
    """
    XOR a binary key with a binary text string (same length).
    Example: key='1010', text='1100' -> '0110'
    """
    return "".join(
        str(ord(key) - ord("0") ^ (ord(letter) - ord("0")))
        for key, letter in zip(keys, text)
    )

def generate_seed():
    """Generate random non-zero 5-bit seed for LFSR."""
    seed = [random.randint(0, 1) for _ in range(5)]
    while seed == [0, 0, 0, 0, 0]:
        seed = [random.randint(0, 1) for _ in range(5)]
    return seed

def lfsr(n):
    """
    Linear Feedback Shift Register key generator.
    Returns a pseudo-random binary string of length n.
    """
    seed = generate_seed()
    return_key = ""
    for round in range(n):
        if round != 0 and n > 10 and round % 10 == 0:
            seed = generate_seed()
        new_bit = seed[4] ^ seed[2] ^ seed[0]
        return_key += str(new_bit)
        if round == n - 1:
            break
        for shift in range(4, -1, -1):
            if shift == 0:
                seed[0] = new_bit
            else:
                seed[shift] = seed[shift - 1]
    return return_key

# =============================
# === FILE I/O HELPERS ===
# =============================

def save_file(path: str, data):
    """
    Save bytes or text to file. Creates folders if needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, (bytes, bytearray)):
        with open(path, "wb") as f:
            f.write(data)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(data))

def load_file(path: str) -> bytes:
    """
    Load any file as bytes (binary mode).
    """
    with open(path, "rb") as f:
        return f.read()

# =============================
# === OPTIONAL: RANDOM DNA KEY SEED ===
# =============================

def generate_random_dna(length=50):
    """
    Generate a random DNA sequence (A/G/C/T) of given length.
    Could be printed to a physical card, stored, or synthesized.
    """
    bases = ["A", "C", "G", "T"]
    return "".join(random.choice(bases) for _ in range(length))
