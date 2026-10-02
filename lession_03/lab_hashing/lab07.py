
# ============================================================
# LAB 06 — SHA-256 FROM SCRATCH
# STEP 1: PADDING
# STEP 2: BLOCK SPLITTING AND WORD CONVERSION
# ============================================================

WORD_SIZE = 32
BLOCK_SIZE = 64
MASK = 0xFFFFFFFF


# ============================================================
# STEP 1 — SHA-256 PADDING
# ============================================================

def sha256_padding(message: bytes) -> bytes:
    """
    Apply SHA-256 padding to a message.

    Padding:
        message + 1 bit + zeros + 64-bit original length
    """

    # Original message length in bits
    original_length = len(message) * 8

    # Append the bit 1, followed by seven zeros
    padded = message + b"\x80"

    # Append zero bytes until length % 64 == 56
    while len(padded) % BLOCK_SIZE != 56:
        padded += b"\x00"

    # Append original length as a 64-bit big-endian integer
    padded += original_length.to_bytes(8, byteorder="big")

    return padded


# ============================================================
# STEP 2.1 — SPLIT INTO 512-BIT BLOCKS
# ============================================================

def split_blocks(padded_message: bytes) -> list[bytes]:
    """
    Split padded message into 64-byte blocks.
    """

    if len(padded_message) % BLOCK_SIZE != 0:
        raise ValueError(
            "Padded message must be a multiple of 64 bytes"
        )

    blocks = []

    for i in range(0, len(padded_message), BLOCK_SIZE):
        block = padded_message[i:i + BLOCK_SIZE]
        blocks.append(block)

    return blocks


# ============================================================
# STEP 2.2 — CONVERT BLOCK INTO 16 WORDS
# ============================================================

def block_to_words(block: bytes) -> list[int]:
    """
    Convert a 64-byte block into 16 big-endian 32-bit words.
    """

    if len(block) != BLOCK_SIZE:
        raise ValueError(
            "A SHA-256 block must contain exactly 64 bytes"
        )

    words = []

    for i in range(0, BLOCK_SIZE, 4):

        four_bytes = block[i:i + 4]

        word = int.from_bytes(
            four_bytes,
            byteorder="big"
        )

        words.append(word)

    return words


# ============================================================
# TEST 1 — PADDING
# ============================================================

def test_padding():

    messages = [
        b"",
        b"a",
        b"abc",
        b"hello",
        b"A" * 55,
        b"A" * 56,
        b"A" * 64,
    ]

    print("\n========== PADDING TEST ==========")

    for message in messages:

        padded = sha256_padding(message)

        print("Original length:", len(message))
        print("Padded length:", len(padded))
        print("Number of blocks:", len(padded) // 64)
        print("Multiple of 64:", len(padded) % 64 == 0)
        print("Last 8 bytes:", padded[-8:].hex())

        assert len(padded) % 64 == 0

        print("-" * 40)


# ============================================================
# TEST 2 — BLOCK SPLITTING
# ============================================================

def test_split_blocks():

    message = b"abc"

    padded = sha256_padding(message)

    blocks = split_blocks(padded)

    print("\n========== BLOCK SPLITTING TEST ==========")

    print("Number of blocks:", len(blocks))

    for index, block in enumerate(blocks):

        print(f"Block {index}: {len(block)} bytes")

        assert len(block) == 64


# ============================================================
# TEST 3 — WORD CONVERSION
# ============================================================

def test_block_to_words():

    message = b"abc"

    padded = sha256_padding(message)

    blocks = split_blocks(padded)

    words = block_to_words(blocks[0])

    print("\n========== WORD CONVERSION TEST ==========")

    print("Number of words:", len(words))

    for i, word in enumerate(words):

        print(f"W[{i:02}] = 0x{word:08x}")

        assert 0 <= word <= MASK

    assert len(words) == 16

    # Verify known values for padded "abc"
    assert words[0] == 0x61626380
    assert words[15] == 0x00000018

    print("\nAll word conversion tests passed!")




# ============================================================
# STEP 3.1 — BITWISE OPERATIONS
# ============================================================

WORD_SIZE = 32
MASK = 0xFFFFFFFF


def rotr(x: int, n: int) -> int:
    """
    Rotate a 32-bit integer right by n bits.
    """

    return ((x >> n) | (x << (32 - n))) & MASK


def shr(x: int, n: int) -> int:
    """
    Logical right shift.
    """

    return x >> n


# ============================================================
# STEP 3.2 — SMALL SIGMA FUNCTIONS
# ============================================================

def sigma0(x: int) -> int:

    return (
        rotr(x, 7)
        ^ rotr(x, 18)
        ^ shr(x, 3)
    )


def sigma1(x: int) -> int:

    return (
        rotr(x, 17)
        ^ rotr(x, 19)
        ^ shr(x, 10)
    )


# ============================================================
# STEP 3.1 — BITWISE OPERATIONS
# ============================================================

WORD_SIZE = 32
MASK = 0xFFFFFFFF


def rotr(x: int, n: int) -> int:
    """
    Rotate a 32-bit integer right by n bits.
    """

    return ((x >> n) | (x << (32 - n))) & MASK


def shr(x: int, n: int) -> int:
    """
    Logical right shift.
    """

    return x >> n


# ============================================================
# STEP 3.2 — SMALL SIGMA FUNCTIONS
# ============================================================

def sigma0(x: int) -> int:

    return (
        rotr(x, 7)
        ^ rotr(x, 18)
        ^ shr(x, 3)
    )


def sigma1(x: int) -> int:

    return (
        rotr(x, 17)
        ^ rotr(x, 19)
        ^ shr(x, 10)
    )

def test_bitwise():

    x = 0x12345678

    print("Original:", hex(x))

    print("ROTR 4:", hex(rotr(x, 4)))

    print("SHR 4:", hex(shr(x, 4)))

    print("Sigma0:", hex(sigma0(x)))

    print("Sigma1:", hex(sigma1(x)))


if __name__ == "__main__":
    test_bitwise()
# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_padding()

    test_split_blocks()

    test_block_to_words()

    test_bitwise()
