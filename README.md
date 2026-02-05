# DNA-Based Encryption with Adaptive Huffman Coding and AES

## 📌 Project Overview
This project implements a **hybrid cryptographic framework** that combines **Adaptive Huffman compression**, **AES encryption**, **DNA-based encoding**, and **Error Correction Codes (ECC)** to provide enhanced data security.  
The approach introduces a bio-inspired DNA transformation layer over traditional cryptography to increase resistance against cryptanalysis and statistical attacks.


## 🔐 Key Features
- Adaptive Huffman compression for redundancy reduction  
- AES-based symmetric encryption for confidentiality  
- DNA sequence encoding (A, T, C, G) for bio-inspired obfuscation  
- Error Correction Codes (ECC) for reliable data recovery  
- Supports encryption and decryption of **text and image files**

## 📁 Project Folder Structure


├── adaptiveHuffman.py     # Adaptive Huffman compression and decompression
├── aes_dna.py             # AES encryption integrated with DNA encoding
├── aes_utils.py           # Utility functions for AES operations
├── DNA.py                 # DNA encoding and decoding logic
├── dna_codec.py           # Binary-to-DNA and DNA-to-binary conversion
├── dna_utils.py           # Helper functions for DNA processing
├── ecc.py                 # Error Correction Code implementation
├── ecc_rs.py              # Reed–Solomon based ECC
├── ecc_utils.py           # ECC utility functions
├── error_simulator.py     # Simulates errors in DNA sequences
├── oligo_packer.py        # DNA oligonucleotide packing logic
├── utils.py               # Common helper utilities
├── main.py                # Main execution file (encryption & decryption)
├── **pycache**/           # Python cache files



## ⚙️ Tech Stack
- **Programming Language:** Python  
- **Cryptography:** AES (symmetric encryption)  
- **Compression:** Adaptive Huffman Coding  
- **Bio-inspired Security:** DNA Encoding (A, T, C, G)  
- **Error Handling:** Reed–Solomon Error Correction Codes  

## 🧠 System Methodology
1. Input data (text or image) is compressed using Adaptive Huffman coding  
2. Compressed data is encrypted using AES  
3. Encrypted binary data is mapped into DNA nucleotide sequences  
4. ECC is applied to handle transmission or storage errors  
5. Decryption reverses the process to recover original data losslessly  

---

## ▶️ How to Run the Project

### Step 1: Run the Main Program
```bash
python main.py
````

### Step 2: Choose Operation

* Press `1` for Encryption
* Press `2` for Decryption

### Step 3: Select File Type

* Text file (`.txt`)
* Image file (`.jpg`, `.png`)



## 🔍 Example DNA Encoding Rule

```
00 → A  
01 → T  
10 → C  
11 → G  
```



## 📈 Applications

* Secure data transmission
* Bio-inspired cryptographic systems
* Multimedia (text & image) encryption
* Research in DNA cryptography and cyber security

---

## 🚀 Future Enhancements

* Integration with quantum-resistant cryptography
* Real DNA storage and retrieval support
* GUI-based encryption/decryption interface
* Support for additional file formats


## 👩‍💻 Author

**Y. Sai Sree Nikhitha**
Cyber Security and Application Security


## 📄 License

This project is licensed under the **Apache 2.0 License**.


## 🔗 GitHub Repository

[https://github.com/22mic0103nikhitha](https://github.com/22mic0103nikhitha)


Just tell me 👍
```
