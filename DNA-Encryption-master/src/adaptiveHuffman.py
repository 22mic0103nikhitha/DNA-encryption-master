import heapq
from collections import defaultdict
from io import BytesIO

# Node for Huffman Tree
class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

# Build Huffman Tree
def build_tree(data):
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1
    heap = [Node(f, s) for s, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(n1.freq + n2.freq, left=n1, right=n2)
        heapq.heappush(heap, merged)
    return heap[0]

# Build Huffman Codes from Tree
def build_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node.symbol is not None:
        codebook[node.symbol] = prefix
    else:
        build_codes(node.left, prefix + "0", codebook)
        build_codes(node.right, prefix + "1", codebook)
    return codebook

# Compress Function
def compress(data):
    """
    Compress input text or bytes using Huffman coding.
    Returns (compressed_bytes, codebook, padding_bits)
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not data:
        return b'', {}, 0

    root = build_tree(data)
    codes = build_codes(root)
    encoded_bits = ''.join(codes[b] for b in data)

    # Pad to make length multiple of 8
    extra = 8 - len(encoded_bits) % 8
    encoded_bits += '0' * extra

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        encoded_bytes.append(int(encoded_bits[i:i+8], 2))
    return bytes(encoded_bytes), codes, extra

# Decompress Function
def decompress(encoded_bytes, codes, extra):
    """
    Decompress using provided Huffman codebook and padding bits.
    Returns original text (UTF-8 string).
    """
    if not encoded_bytes or not codes:
        return ""

    # Reverse the codebook for decoding
    rev = {v: k for k, v in codes.items()}
    bits = ''.join(f"{byte:08b}" for byte in encoded_bytes)
    bits = bits[:-extra] if extra else bits

    buffer = ''
    result = BytesIO()
    for bit in bits:
        buffer += bit
        if buffer in rev:
            result.write(bytes([rev[buffer]]))
            buffer = ''
    output = result.getvalue()
    try:
        return output.decode('utf-8')  # for text
    except UnicodeDecodeError:
        return output  # for binary/image files

