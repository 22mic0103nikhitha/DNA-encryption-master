import os
import base64
import json
from adaptiveHuffman import compress, decompress
from aes_utils import aes_encrypt, aes_decrypt
from ecc_utils import add_ecc, decode_ecc
from dna_utils import bytes_to_dna, dna_to_bytes
from utils import CIPHER_PATH, KEY_PATH, DECRYPT_PATH, save_file, load_file


def encrypt_text():
    ans = input("What do you want to encrypt? \nPress 1 for std input, press 2 for file: ").strip()

    if ans == "1":
        text = input("Enter your message to encrypt: ").encode()
        compressed, codes, extra = compress(text)
        ciphertext, key, nonce, tag = aes_encrypt(compressed)
        cipher_with_ecc = add_ecc(ciphertext)
        dna_seq = bytes_to_dna(cipher_with_ecc)

        save_file(CIPHER_PATH, dna_seq)

        meta = {
            "key": base64.b64encode(key).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "tag": base64.b64encode(tag).decode(),
            "codes": codes,
            "extra": extra
        }
        save_file(KEY_PATH, json.dumps(meta).encode())

        print("\nEncryption complete.")
        print(f"Cipher saved: {CIPHER_PATH}")
        print(f"Metadata saved: {KEY_PATH}")

    elif ans == "2":
        file_path = input("Enter your file name. Ex: '../example/test.txt' or '../example/test.jpg'\n").strip()
        if not os.path.isfile(file_path):
            print("File not found:", file_path)
            exit(1)

        data = load_file(file_path)
        compressed, codes, extra = compress(data)
        ciphertext, key, nonce, tag = aes_encrypt(compressed)
        cipher_with_ecc = add_ecc(ciphertext)
        dna_seq = bytes_to_dna(cipher_with_ecc)

        save_file(CIPHER_PATH, dna_seq)

        meta = {
            "key": base64.b64encode(key).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "tag": base64.b64encode(tag).decode(),
            "codes": codes,
            "extra": extra
        }
        save_file(KEY_PATH, json.dumps(meta).encode())

        print("\nEncryption complete.")
        print(f"Cipher saved: {CIPHER_PATH}")
        print(f"Key and metadata saved: {KEY_PATH}")

    else:
        print("Invalid input!")


def load_metadata_safe():
    """Loads metadata and supports both new JSON format and old binary format."""
    key_data = load_file(KEY_PATH)

    # Try JSON (new format)
    try:
        meta = json.loads(key_data)
        key = base64.b64decode(meta["key"])
        nonce = base64.b64decode(meta["nonce"])
        tag = base64.b64decode(meta["tag"])
        codes = meta["codes"]
        extra = meta["extra"]

        # 🔽 Convert JSON string keys back to int if needed
        if isinstance(codes, dict):
            fixed_codes = {}
            for k, v in codes.items():
                try:
                    fixed_codes[int(k)] = v
                except ValueError:
                    fixed_codes[k] = v
            codes = fixed_codes

        return key, nonce, tag, codes, extra

    except Exception:
        # Try legacy format (binary + "|" separator)
        try:
            parts = key_data.split(b"|")
            if len(parts) < 5:
                raise ValueError("Incomplete legacy metadata.")

            key = parts[0]
            nonce = parts[1]
            tag = parts[2]
            codes = eval(parts[3].decode(errors="ignore"))
            extra = eval(parts[4].decode(errors="ignore"))

            # Auto-upgrade legacy metadata to JSON format
            meta = {
                "key": base64.b64encode(key).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "tag": base64.b64encode(tag).decode(),
                "codes": codes,
                "extra": extra
            }
            save_file(KEY_PATH, json.dumps(meta).encode())
            print("✅ Legacy metadata detected and upgraded to JSON format.")
            return key, nonce, tag, codes, extra

        except Exception as e:
            print("❌ Failed to load metadata (corrupted or incompatible):", e)
            exit(1)



def decrypt_text_or_image(ans):
    if not os.path.isfile(CIPHER_PATH):
        print("File not found:", CIPHER_PATH)
        exit(1)
    if not os.path.isfile(KEY_PATH):
        print("File not found:", KEY_PATH)
        exit(1)

    key, nonce, tag, codes, extra = load_metadata_safe()

    dna_seq = load_file(CIPHER_PATH).decode()
    cipher_with_ecc = dna_to_bytes(dna_seq)
    corrected = decode_ecc(cipher_with_ecc)
    decrypted = aes_decrypt(corrected, key, nonce, tag)
    plain = decompress(decrypted, codes, extra)

    if ans == "1":
        save_file(DECRYPT_PATH + "PlainTextResult.txt", plain)
        print(f"\nDecryption complete.\nDecoded message saved to '{DECRYPT_PATH}PlainTextResult.txt'")
    elif ans == "2":
        save_file(DECRYPT_PATH + "DecodedImage.png", plain)
        print(f"\nDecryption complete.\nDecoded image saved to '{DECRYPT_PATH}DecodedImage.png'")
    else:
        print("Invalid input!")


if __name__ == "__main__":
    print("Encrypt or decrypt a message?")
    EncrypOrDecrypt = input("Press 1 for encryption, press 2 for decryption: ").strip()

    if EncrypOrDecrypt == "1":
        encrypt_text()
    elif EncrypOrDecrypt == "2":
        ans = input("What do you want to decrypt? \nPress 1 for .txt file, press 2 for image file: ").strip()
        decrypt_text_or_image(ans)
    else:
        print("Invalid input!")
